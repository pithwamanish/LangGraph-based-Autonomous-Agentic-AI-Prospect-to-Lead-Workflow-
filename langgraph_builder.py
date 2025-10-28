"""
LangGraphBuilder - Dynamic LangGraph construction and execution system.

This module provides the core functionality for building and executing
LangGraph workflows from JSON configuration files.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

import structlog
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing_extensions import TypedDict

from agents import (
    ProspectSearchAgent,
    DataEnrichmentAgent,
    ScoringAgent,
    OutreachContentAgent,
    OutreachExecutorAgent,
    ResponseTrackerAgent,
    FeedbackTrainerAgent
)


class WorkflowState(TypedDict):
    """State schema for the workflow."""
    workflow_id: str
    start_time: str
    current_step: Optional[str]
    execution_log: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    results: Dict[str, Any]
    end_time: Optional[str]
    duration: Optional[float]


class LangGraphBuilder:
    """
    Builder class for creating and executing LangGraph workflows from JSON configuration.
    
    This class handles:
    - Loading and validating workflow JSON
    - Dynamic agent instantiation
    - Graph construction with proper edges
    - Workflow execution with state management
    - Error handling and logging
    """
    
    def __init__(self, workflow_file: str = "workflow.json", env_file: str = ".env"):
        """
        Initialize the LangGraphBuilder.
        
        Args:
            workflow_file: Path to the workflow JSON file
            env_file: Path to the environment variables file
        """
        self.workflow_file = workflow_file
        self.env_file = env_file
        self.workflow_config = None
        self.agents = {}
        self.graph = None
        self.logger = structlog.get_logger()
        
        # Load environment variables
        self._load_environment()
        
        # Load workflow configuration
        self._load_workflow()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            self.logger.info("Environment variables loaded", env_file=self.env_file)
        else:
            self.logger.warning("Environment file not found", env_file=self.env_file)
    
    def _load_workflow(self) -> None:
        """Load and validate workflow configuration from JSON file."""
        try:
            with open(self.workflow_file, 'r') as f:
                self.workflow_config = json.load(f)
            
            self.logger.info(
                "Workflow loaded successfully",
                workflow_name=self.workflow_config.get("workflow_name"),
                steps_count=len(self.workflow_config.get("steps", []))
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow file: {e}")
    
    def build_graph(self) -> StateGraph:
        """
        Build the LangGraph from the workflow configuration.
        
        Returns:
            Configured StateGraph ready for execution
        """
        self.logger.info("Building LangGraph from workflow configuration")
        
        # Create the state graph
        self.graph = StateGraph(WorkflowState)
        
        # Add nodes for each step
        for step in self.workflow_config.get("steps", []):
            self._add_node(step)
        
        # Add edges based on next_steps configuration
        self._add_edges()
        
        # Compile the graph
        compiled_graph = self.graph.compile()
        
        self.logger.info("LangGraph built successfully", nodes_count=len(self.agents))
        
        # Store the compiled graph
        self.graph = compiled_graph
        
        return compiled_graph
    
    def _create_initial_state(self) -> Dict[str, Any]:
        """
        Create the initial state for the workflow.
        
        Returns:
            Initial state dictionary
        """
        return {
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "current_step": None,
            "execution_log": [],
            "errors": [],
            "results": {}
        }
    
    def _add_node(self, step_config: Dict[str, Any]) -> None:
        """
        Add a node to the graph based on step configuration.
        
        Args:
            step_config: Step configuration from workflow JSON
        """
        step_id = step_config.get("id")
        agent_type = step_config.get("agent")
        
        if not step_id or not agent_type:
            raise ValueError("Step must have 'id' and 'agent' fields")
        
        # Create agent instance
        agent = self._create_agent(step_config)
        self.agents[step_id] = agent
        
        # Add node to graph
        self.graph.add_node(step_id, self._create_node_function(agent, step_id))
        
        self.logger.info("Node added", step_id=step_id, agent_type=agent_type)
    
    def _create_agent(self, step_config: Dict[str, Any]):
        """
        Create an agent instance based on step configuration.
        
        Args:
            step_config: Step configuration
            
        Returns:
            Agent instance
        """
        agent_type = step_config.get("agent")
        agent_id = step_config.get("id")
        instructions = step_config.get("instructions", "")
        tools = self._process_tools(step_config.get("tools", []))
        output_schema = step_config.get("output_schema", {})
        
        # Map agent types to classes
        agent_classes = {
            "ProspectSearchAgent": ProspectSearchAgent,
            "DataEnrichmentAgent": DataEnrichmentAgent,
            "ScoringAgent": ScoringAgent,
            "OutreachContentAgent": OutreachContentAgent,
            "OutreachExecutorAgent": OutreachExecutorAgent,
            "ResponseTrackerAgent": ResponseTrackerAgent,
            "FeedbackTrainerAgent": FeedbackTrainerAgent
        }
        
        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = agent_classes[agent_type]
        
        return agent_class(
            agent_id=agent_id,
            instructions=instructions,
            tools=tools,
            output_schema=output_schema,
            logger=self.logger
        )
    
    def _process_tools(self, tools_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process tool configurations and substitute environment variables.
        
        Args:
            tools_config: List of tool configurations
            
        Returns:
            Processed tool configurations
        """
        processed_tools = []
        
        for tool in tools_config:
            processed_tool = tool.copy()
            processed_tool["config"] = self._substitute_env_vars(tool.get("config", {}))
            processed_tools.append(processed_tool)
        
        return processed_tools
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute environment variables in configuration values.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with substituted values
        """
        substituted = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                # Replace {{VAR_NAME}} with environment variable
                substituted[key] = self._substitute_string(value)
            elif isinstance(value, dict):
                substituted[key] = self._substitute_env_vars(value)
            else:
                substituted[key] = value
        
        return substituted
    
    def _substitute_string(self, text: str) -> str:
        """
        Substitute environment variables in a string.
        
        Args:
            text: String that may contain {{VAR_NAME}} patterns
            
        Returns:
            String with substituted values
        """
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)
    
    def _create_node_function(self, agent, step_id: str):
        """
        Create a node function for the graph.
        
        Args:
            agent: Agent instance
            step_id: Step identifier
            
        Returns:
            Node function
        """
        def node_function(state: WorkflowState) -> WorkflowState:
            """Execute a single node in the workflow."""
            try:
                self.logger.info("Executing node", step_id=step_id)
                
                # Prepare input data
                input_data = self._prepare_node_input(state, step_id)
                
                # Execute agent
                result = agent.execute(input_data)
                
                # Update state with results
                new_state = state.copy()
                new_state["current_step"] = step_id
                new_state["execution_log"] = state["execution_log"] + [{
                    "step_id": step_id,
                    "timestamp": datetime.now().isoformat(),
                    "success": result.success,
                    "execution_time": result.execution_time
                }]
                
                if result.success:
                    new_state["results"] = {**state["results"], step_id: result.data}
                    self.logger.info("Node executed successfully", step_id=step_id)
                else:
                    new_state["errors"] = state["errors"] + [{
                        "step_id": step_id,
                        "error": result.error,
                        "timestamp": datetime.now().isoformat()
                    }]
                    self.logger.error("Node execution failed", step_id=step_id, error=result.error)
                
                return new_state
                
            except Exception as e:
                self.logger.error("Node execution exception", step_id=step_id, error=str(e))
                
                new_state = state.copy()
                new_state["errors"] = state["errors"] + [{
                    "step_id": step_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
                
                return new_state
        
        return node_function
    
    def _prepare_node_input(self, state: WorkflowState, step_id: str) -> Dict[str, Any]:
        """
        Prepare input data for a node based on its configuration.
        
        Args:
            state: Current workflow state
            step_id: Step identifier
            
        Returns:
            Prepared input data
        """
        # Find step configuration
        step_config = None
        for step in self.workflow_config.get("steps", []):
            if step.get("id") == step_id:
                step_config = step
                break
        
        if not step_config:
            raise ValueError(f"Step configuration not found: {step_id}")
        
        # Get input configuration
        inputs = step_config.get("inputs", {})
        prepared_inputs = {}
        
        for input_key, input_value in inputs.items():
            if isinstance(input_value, str) and input_value.startswith("{{") and input_value.endswith("}}"):
                # Reference to another step's output
                reference = input_value[2:-2]  # Remove {{ and }}
                if "." in reference:
                    step_ref, output_key = reference.split(".", 1)
                    if step_ref in state.get("results", {}):
                        prepared_inputs[input_key] = state["results"][step_ref].get(output_key)
                    else:
                        prepared_inputs[input_key] = None
                else:
                    prepared_inputs[input_key] = state.get("results", {}).get(reference)
            elif input_value == "{{config.scoring}}":
                prepared_inputs[input_key] = self.workflow_config.get("config", {}).get("scoring", {})
            elif input_value == "{{config.outreach.persona}}":
                prepared_inputs[input_key] = self.workflow_config.get("config", {}).get("outreach", {}).get("persona", "SDR")
            elif input_value == "{{config.outreach.tone}}":
                prepared_inputs[input_key] = self.workflow_config.get("config", {}).get("outreach", {}).get("tone", "friendly")
            else:
                prepared_inputs[input_key] = input_value
        
        return prepared_inputs
    
    def _add_edges(self) -> None:
        """Add edges to the graph based on next_steps configuration."""
        for step in self.workflow_config.get("steps", []):
            step_id = step.get("id")
            next_steps = step.get("next_steps", [])
            
            if not next_steps:
                # If no next steps, connect to END
                self.graph.add_edge(step_id, END)
            else:
                # Connect to first next step (for now, supporting only sequential flows)
                if len(next_steps) > 0:
                    self.graph.add_edge(step_id, next_steps[0])
        
        # Add entry point
        first_step = self.workflow_config.get("steps", [{}])[0].get("id")
        if first_step:
            self.graph.set_entry_point(first_step)
    
    def execute_workflow(self, initial_inputs: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Execute the complete workflow.
        
        Args:
            initial_inputs: Optional initial inputs for the workflow
            
        Returns:
            Final workflow state
        """
        if not self.graph:
            self.build_graph()
        
        # Prepare initial state
        initial_state = self._create_initial_state()
        if initial_inputs:
            # Merge initial inputs into state
            for key, value in initial_inputs.items():
                if key in initial_state:
                    initial_state[key] = value
        
        self.logger.info("Starting workflow execution", workflow_id=initial_state["workflow_id"])
        
        try:
            # Execute the workflow
            final_state = self.graph.invoke(initial_state)
            
            # Add completion metadata
            final_state["end_time"] = datetime.now().isoformat()
            final_state["duration"] = (
                datetime.fromisoformat(final_state["end_time"]) - 
                datetime.fromisoformat(final_state["start_time"])
            ).total_seconds()
            
            self.logger.info(
                "Workflow execution completed",
                workflow_id=final_state["workflow_id"],
                duration=final_state["duration"],
                errors_count=len(final_state.get("errors", []))
            )
            
            return final_state
            
        except Exception as e:
            self.logger.error("Workflow execution failed", error=str(e))
            raise
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow configuration.
        
        Returns:
            Workflow summary
        """
        steps = self.workflow_config.get("steps", [])
        
        return {
            "workflow_name": self.workflow_config.get("workflow_name"),
            "description": self.workflow_config.get("description"),
            "version": self.workflow_config.get("version"),
            "total_steps": len(steps),
            "steps": [
                {
                    "id": step.get("id"),
                    "agent": step.get("agent"),
                    "next_steps": step.get("next_steps", [])
                }
                for step in steps
            ],
            "config": self.workflow_config.get("config", {})
        }


def main():
    """Main function for testing the LangGraphBuilder."""
    try:
        # Initialize builder
        builder = LangGraphBuilder()
        
        # Print workflow summary
        summary = builder.get_workflow_summary()
        print("Workflow Summary:")
        print(json.dumps(summary, indent=2))
        
        # Build and execute workflow
        print("\nBuilding and executing workflow...")
        final_state = builder.execute_workflow()
        
        print("\nExecution completed!")
        print(f"Workflow ID: {final_state['workflow_id']}")
        print(f"Duration: {final_state['duration']:.2f} seconds")
        print(f"Steps executed: {len(final_state['execution_log'])}")
        print(f"Errors: {len(final_state.get('errors', []))}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
