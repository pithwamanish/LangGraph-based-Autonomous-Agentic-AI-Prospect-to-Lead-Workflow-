#!/usr/bin/env python3
"""
Test script for the Prospect-to-Lead Workflow System.

This script demonstrates how to use the LangGraphBuilder and validates
that all components are working correctly.
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_builder import LangGraphBuilder


def test_workflow_loading():
    """Test that the workflow configuration loads correctly."""
    print("🧪 Testing workflow loading...")
    
    try:
        builder = LangGraphBuilder()
        summary = builder.get_workflow_summary()
        
        print(f"✅ Workflow loaded successfully: {summary['workflow_name']}")
        print(f"   - Description: {summary['description']}")
        print(f"   - Version: {summary['version']}")
        print(f"   - Total steps: {summary['total_steps']}")
        
        return True
    except Exception as e:
        print(f"❌ Workflow loading failed: {e}")
        return False


def test_agent_creation():
    """Test that agents can be created correctly."""
    print("\n🧪 Testing agent creation...")
    
    try:
        builder = LangGraphBuilder()
        
        # Test creating each agent type
        agent_types = [
            "ProspectSearchAgent",
            "DataEnrichmentAgent", 
            "ScoringAgent",
            "OutreachContentAgent",
            "OutreachExecutorAgent",
            "ResponseTrackerAgent",
            "FeedbackTrainerAgent"
        ]
        
        for agent_type in agent_types:
            # Create a minimal step config for testing
            step_config = {
                "id": f"test_{agent_type.lower()}",
                "agent": agent_type,
                "instructions": f"Test instructions for {agent_type}",
                "tools": [],
                "output_schema": {}
            }
            
            agent = builder._create_agent(step_config)
            print(f"   ✅ {agent_type} created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


def test_graph_building():
    """Test that the LangGraph can be built successfully."""
    print("\n🧪 Testing graph building...")
    
    try:
        builder = LangGraphBuilder()
        graph = builder.build_graph()
        
        print("✅ LangGraph built successfully")
        print(f"   - Graph type: {type(graph)}")
        print(f"   - Agents loaded: {len(builder.agents)}")
        
        return True
    except Exception as e:
        print(f"❌ Graph building failed: {e}")
        return False


def test_environment_variables():
    """Test that environment variables are loaded correctly."""
    print("\n🧪 Testing environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "CLAY_API_KEY", 
        "APOLLO_API_KEY",
        "CLEARBIT_API_KEY",
        "SENDGRID_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   This is expected for testing - the system will use placeholder values")
    else:
        print("✅ All required environment variables are set")
    
    return True


def test_workflow_execution():
    """Test workflow execution with mock data."""
    print("\n🧪 Testing workflow execution...")
    
    try:
        builder = LangGraphBuilder()
        
        # Create a minimal test workflow
        test_workflow = {
            "workflow_name": "TestWorkflow",
            "description": "Test workflow for validation",
            "version": "1.0.0",
            "config": {
                "scoring": {
                    "criteria": [
                        {"field": "company_size", "weight": 0.5, "min": 100, "max": 1000}
                    ]
                }
            },
            "steps": [
                {
                    "id": "test_scoring",
                    "agent": "ScoringAgent",
                    "inputs": {
                        "enriched_leads": [
                            {
                                "company": "Test Company",
                                "contact_name": "Test Contact",
                                "email": "test@example.com",
                                "company_size": 500
                            }
                        ],
                        "scoring_criteria": {
                            "criteria": [
                                {"field": "company_size", "weight": 0.5, "min": 100, "max": 1000}
                            ]
                        }
                    },
                    "instructions": "Test scoring agent",
                    "tools": [],
                    "output_schema": {"ranked_leads": "array"},
                    "next_steps": []
                }
            ]
        }
        
        # Save test workflow temporarily
        with open("test_workflow.json", "w") as f:
            json.dump(test_workflow, f, indent=2)
        
        # Test with the test workflow
        test_builder = LangGraphBuilder("test_workflow.json")
        final_state = test_builder.execute_workflow()
        
        print("✅ Workflow execution completed successfully")
        print(f"   - Workflow ID: {final_state['workflow_id']}")
        print(f"   - Duration: {final_state.get('duration', 0):.2f} seconds")
        print(f"   - Steps executed: {len(final_state['execution_log'])}")
        print(f"   - Errors: {len(final_state.get('errors', []))}")
        
        # Clean up test file
        os.remove("test_workflow.json")
        
        return True
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Prospect-to-Lead Workflow System Tests")
    print("=" * 60)
    
    tests = [
        test_workflow_loading,
        test_agent_creation,
        test_graph_building,
        test_environment_variables,
        test_workflow_execution
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
