#!/usr/bin/env python3
"""
Demo script for the Prospect-to-Lead Workflow System.

This script demonstrates the key features of the system including:
- Workflow configuration loading
- Dynamic agent creation
- LangGraph execution
- Performance monitoring
"""

import json
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_builder import LangGraphBuilder


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)


def print_step(step, description):
    """Print a formatted step."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)


def demo_workflow_summary():
    """Demonstrate workflow summary functionality."""
    print_section("Workflow Configuration Summary")
    
    try:
        builder = LangGraphBuilder()
        summary = builder.get_workflow_summary()
        
        print(f"Workflow Name: {summary['workflow_name']}")
        print(f"Description: {summary['description']}")
        print(f"Version: {summary['version']}")
        print(f"Total Steps: {summary['total_steps']}")
        
        print("\nWorkflow Steps:")
        for i, step in enumerate(summary['steps'], 1):
            print(f"  {i}. {step['id']} ({step['agent']})")
            if step['next_steps']:
                print(f"     → Next: {', '.join(step['next_steps'])}")
        
        print(f"\nConfiguration:")
        print(f"  Scoring Criteria: {len(summary['config'].get('scoring', {}).get('criteria', []))} rules")
        print(f"  Outreach Persona: {summary['config'].get('outreach', {}).get('persona', 'N/A')}")
        print(f"  Outreach Tone: {summary['config'].get('outreach', {}).get('tone', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_agent_creation():
    """Demonstrate agent creation functionality."""
    print_section("Agent Creation and Initialization")
    
    try:
        builder = LangGraphBuilder()
        
        # Show agent types
        agent_types = [
            "ProspectSearchAgent",
            "DataEnrichmentAgent", 
            "ScoringAgent",
            "OutreachContentAgent",
            "OutreachExecutorAgent",
            "ResponseTrackerAgent",
            "FeedbackTrainerAgent"
        ]
        
        print("Available Agent Types:")
        for i, agent_type in enumerate(agent_types, 1):
            print(f"  {i}. {agent_type}")
        
        # Test creating a sample agent
        print("\nTesting Agent Creation:")
        step_config = {
            "id": "demo_scoring",
            "agent": "ScoringAgent",
            "instructions": "Demo scoring agent for testing",
            "tools": [],
            "output_schema": {"ranked_leads": "array"}
        }
        
        agent = builder._create_agent(step_config)
        print(f"✅ Created {agent.__class__.__name__} with ID: {agent.agent_id}")
        print(f"   Instructions: {agent.instructions}")
        print(f"   Tools: {len(agent.tools)}")
        print(f"   Output Schema: {list(agent.output_schema.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_graph_building():
    """Demonstrate graph building functionality."""
    print_section("LangGraph Building and Compilation")
    
    try:
        builder = LangGraphBuilder()
        
        print("Building LangGraph from workflow configuration...")
        graph = builder.build_graph()
        
        print(f"✅ Graph built successfully!")
        print(f"   Graph Type: {type(graph).__name__}")
        print(f"   Agents Loaded: {len(builder.agents)}")
        
        print("\nAgent Registry:")
        for step_id, agent in builder.agents.items():
            print(f"  - {step_id}: {agent.__class__.__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_workflow_execution():
    """Demonstrate workflow execution functionality."""
    print_section("Workflow Execution Demo")
    
    try:
        # Create a simple test workflow
        test_workflow = {
            "workflow_name": "DemoWorkflow",
            "description": "Demonstration workflow for testing",
            "version": "1.0.0",
            "config": {
                "scoring": {
                    "criteria": [
                        {"field": "company_size", "weight": 0.6, "min": 100, "max": 1000},
                        {"field": "revenue", "weight": 0.4, "min": 1000000, "max": 100000000}
                    ]
                }
            },
            "steps": [
                {
                    "id": "demo_scoring",
                    "agent": "ScoringAgent",
                    "inputs": {
                        "enriched_leads": [
                            {
                                "company": "Acme Corp",
                                "contact_name": "John Smith",
                                "email": "john@acme.com",
                                "company_size": 500,
                                "revenue": 50000000
                            },
                            {
                                "company": "Beta Inc",
                                "contact_name": "Jane Doe", 
                                "email": "jane@beta.com",
                                "company_size": 200,
                                "revenue": 20000000
                            }
                        ],
                        "scoring_criteria": {
                            "criteria": [
                                {"field": "company_size", "weight": 0.6, "min": 100, "max": 1000},
                                {"field": "revenue", "weight": 0.4, "min": 1000000, "max": 100000000}
                            ]
                        }
                    },
                    "instructions": "Score and rank demo leads",
                    "tools": [],
                    "output_schema": {"ranked_leads": "array"},
                    "next_steps": []
                }
            ]
        }
        
        # Save test workflow
        with open("demo_workflow.json", "w") as f:
            json.dump(test_workflow, f, indent=2)
        
        print("Created demo workflow with 2 sample leads")
        print("  - Acme Corp: 500 employees, $50M revenue")
        print("  - Beta Inc: 200 employees, $20M revenue")
        
        # Execute workflow
        print("\nExecuting workflow...")
        builder = LangGraphBuilder("demo_workflow.json")
        final_state = builder.execute_workflow()
        
        print(f"✅ Workflow executed successfully!")
        print(f"   Workflow ID: {final_state['workflow_id']}")
        print(f"   Duration: {final_state['duration']:.3f} seconds")
        print(f"   Steps Executed: {len(final_state['execution_log'])}")
        print(f"   Errors: {len(final_state.get('errors', []))}")
        
        # Show results
        if 'demo_scoring' in final_state['results']:
            results = final_state['results']['demo_scoring']
            ranked_leads = results.get('ranked_leads', [])
            
            print(f"\nScoring Results:")
            print(f"  Total Leads Processed: {len(ranked_leads)}")
            
            for i, lead in enumerate(ranked_leads, 1):
                print(f"  {i}. {lead.get('company', 'Unknown')}")
                print(f"     Score: {lead.get('total_score', 0):.2f}")
                print(f"     Rank: {lead.get('rank', 'N/A')}")
                print(f"     Percentile: {lead.get('percentile', 0):.1f}%")
        
        # Clean up
        os.remove("demo_workflow.json")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_performance_monitoring():
    """Demonstrate performance monitoring features."""
    print_section("Performance Monitoring and Logging")
    
    print("The system includes comprehensive monitoring features:")
    print("\n📊 Structured Logging:")
    print("  - All operations are logged with structured data")
    print("  - Easy integration with log aggregation systems")
    print("  - Performance metrics and error tracking")
    
    print("\n⏱️  Execution Tracking:")
    print("  - Step-by-step execution logs")
    print("  - Performance timing for each agent")
    print("  - Error tracking and recovery")
    
    print("\n📈 Metrics Collection:")
    print("  - Response rates and engagement metrics")
    print("  - Agent performance statistics")
    print("  - Workflow execution analytics")
    
    print("\n🔍 Reasoning Transparency:")
    print("  - Agent reasoning steps are logged")
    print("  - Decision-making process is transparent")
    print("  - Easy debugging and optimization")
    
    return True


def main():
    """Run the complete demonstration."""
    print("🚀 Prospect-to-Lead Workflow System Demonstration")
    print("Built with LangGraph, LangChain, and modern Python practices")
    
    demos = [
        ("Workflow Summary", demo_workflow_summary),
        ("Agent Creation", demo_agent_creation),
        ("Graph Building", demo_graph_building),
        ("Workflow Execution", demo_workflow_execution),
        ("Performance Monitoring", demo_performance_monitoring)
    ]
    
    passed = 0
    total = len(demos)
    
    for title, demo_func in demos:
        try:
            if demo_func():
                passed += 1
        except Exception as e:
            print(f"❌ Demo '{title}' failed: {e}")
    
    print_section("Demonstration Summary")
    print(f"📊 Results: {passed}/{total} demos completed successfully")
    
    if passed == total:
        print("🎉 All demonstrations completed successfully!")
        print("\n✨ The Prospect-to-Lead Workflow System is ready for production use!")
        print("\nNext steps:")
        print("  1. Set up your API keys in .env file")
        print("  2. Customize workflow.json for your use case")
        print("  3. Run: python langgraph_builder.py")
        return 0
    else:
        print("⚠️  Some demonstrations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
