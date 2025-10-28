"""
Base agent class that all workflow agents inherit from.

Provides common functionality for agent execution, logging, and error handling.
"""

import json
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import structlog
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Standardized input model for agents."""
    data: Dict[str, Any] = Field(..., description="Input data for the agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class AgentOutput(BaseModel):
    """Standardized output model for agents."""
    success: bool = Field(..., description="Whether the agent execution was successful")
    data: Dict[str, Any] = Field(..., description="Output data from the agent")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


class BaseAgent(ABC):
    """
    Abstract base class for all workflow agents.
    
    Provides common functionality for:
    - Input/output validation
    - Error handling and logging
    - Tool management
    - Execution timing
    """
    
    def __init__(
        self,
        agent_id: str,
        instructions: str,
        tools: List[Dict[str, Any]] = None,
        output_schema: Dict[str, Any] = None,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            instructions: Instructions for the agent's behavior
            tools: List of tools available to this agent
            output_schema: Expected output schema for validation
            logger: Structured logger instance
        """
        self.agent_id = agent_id
        self.instructions = instructions
        self.tools = tools or []
        self.output_schema = output_schema or {}
        self.logger = logger or structlog.get_logger()
        
        # Initialize tools
        self._initialized_tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """Initialize all tools for this agent."""
        for tool_config in self.tools:
            tool_name = tool_config.get("name")
            tool_config_data = tool_config.get("config", {})
            
            try:
                tool_instance = self._create_tool(tool_name, tool_config_data)
                self._initialized_tools[tool_name] = tool_instance
                self.logger.info(
                    "Tool initialized",
                    tool_name=tool_name,
                    agent_id=self.agent_id
                )
            except Exception as e:
                self.logger.error(
                    "Failed to initialize tool",
                    tool_name=tool_name,
                    error=str(e),
                    agent_id=self.agent_id
                )
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """
        Create a tool instance based on the tool name and configuration.
        
        This method should be overridden by subclasses to implement
        specific tool creation logic.
        
        Args:
            tool_name: Name of the tool to create
            config: Configuration for the tool
            
        Returns:
            Tool instance
        """
        # Default implementation - subclasses should override
        return {"name": tool_name, "config": config}
    
    def execute(self, input_data: Union[Dict[str, Any], AgentInput]) -> AgentOutput:
        """
        Execute the agent with the given input data.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            AgentOutput with execution results
        """
        start_time = datetime.now()
        
        try:
            # Validate and normalize input
            if isinstance(input_data, dict):
                agent_input = AgentInput(data=input_data)
            else:
                agent_input = input_data
            
            self.logger.info(
                "Agent execution started",
                agent_id=self.agent_id,
                input_keys=list(agent_input.data.keys())
            )
            
            # Execute the agent's main logic
            result_data = self._execute_agent(agent_input)
            
            # Validate output against schema if provided
            if self.output_schema:
                self._validate_output(result_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                "Agent execution completed successfully",
                agent_id=self.agent_id,
                execution_time=execution_time
            )
            
            return AgentOutput(
                success=True,
                data=result_data,
                metadata={
                    "agent_id": self.agent_id,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Agent execution failed: {str(e)}"
            
            self.logger.error(
                "Agent execution failed",
                agent_id=self.agent_id,
                error=error_msg,
                traceback=traceback.format_exc(),
                execution_time=execution_time
            )
            
            return AgentOutput(
                success=False,
                data={},
                error=error_msg,
                metadata={
                    "agent_id": self.agent_id,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
    
    @abstractmethod
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute the agent's main logic.
        
        This method must be implemented by subclasses.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Dictionary containing the agent's output data
        """
        pass
    
    def _validate_output(self, output_data: Dict[str, Any]) -> None:
        """
        Validate output data against the expected schema.
        
        Args:
            output_data: Output data to validate
            
        Raises:
            ValueError: If output doesn't match expected schema
        """
        # Basic validation - can be enhanced with more sophisticated schema validation
        if not isinstance(output_data, dict):
            raise ValueError("Output data must be a dictionary")
        
        # Check required fields from schema
        for field, field_type in self.output_schema.items():
            if field not in output_data:
                raise ValueError(f"Missing required output field: {field}")
    
    def get_tool(self, tool_name: str) -> Any:
        """
        Get an initialized tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance
            
        Raises:
            KeyError: If tool is not found
        """
        if tool_name not in self._initialized_tools:
            raise KeyError(f"Tool '{tool_name}' not found for agent '{self.agent_id}'")
        
        return self._initialized_tools[tool_name]
    
    def log_reasoning(self, step: str, reasoning: str, data: Any = None) -> None:
        """
        Log reasoning steps for transparency and debugging.
        
        Args:
            step: Name of the reasoning step
            reasoning: Reasoning explanation
            data: Optional data related to the reasoning
        """
        self.logger.info(
            "Agent reasoning",
            agent_id=self.agent_id,
            step=step,
            reasoning=reasoning,
            data=data
        )
