#!/usr/bin/env python3
"""
Test script for ProspectSearchAgent.

This script tests the prospect search functionality using Apollo API
to find companies and contacts matching the ICP criteria.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.prospect_search_agent import ProspectSearchAgent
from agents.base_agent import AgentInput


def test_prospect_search_agent():
    """Test Prospect Search Agent functionality."""
    print("🧪 Testing Prospect Search Agent")
    print("=" * 60)
    
    # Check environment variables
    apollo_api_key = os.getenv('APOLLO_API_KEY')
    clay_api_key = os.getenv('CLAY_API_KEY')
    
    if not apollo_api_key:
        print("❌ APOLLO_API_KEY environment variable not set")
        print("   Set it in your .env file to test Apollo API integration")
        return False
    
    print(f"✅ Apollo API Key: {apollo_api_key[:10]}...{apollo_api_key[-4:]}")
    
    if clay_api_key:
        print(f"✅ Clay API Key: {clay_api_key[:10]}...{clay_api_key[-4:]}")
    else:
        print("⚠️  Clay API Key not set (will use Apollo only)")
    
    try:
        # Initialize Prospect Search Agent
        print("\n🔧 Initializing Prospect Search Agent...")
        
        tools = [
            {
                "name": "ApolloAPI",
                "config": {
                    "api_key": apollo_api_key,
                    "endpoint": "https://api.apollo.io/v1/mixed_people/search"
                }
            }
        ]
        
        if clay_api_key:
            tools.append({
                "name": "ClayAPI",
                "config": {
                    "api_key": clay_api_key,
                    "endpoint": "https://api.clay.com/search"
                }
            })
        
        agent = ProspectSearchAgent(
            agent_id="prospect_search",
            instructions="Use Apollo API to search for company and contact data matching ICP. Return structured leads.",
            tools=tools
        )
        
        print("✅ Prospect Search Agent initialized successfully")
        
        # Test 1: Search for prospects with ICP criteria
        print("\n📊 Test 1: Searching for prospects matching ICP...")
        print("   ICP Criteria:")
        print("      Industry: SaaS")
        print("      Location: USA")
        print("      Employee Count: 100-1000")
        print("      Revenue: $20M-$200M")
        print("      Signals: recent_funding, hiring_for_sales")
        
        test_input = AgentInput(
            agent_id="prospect_search",
            data={
                "icp": {
                    "industry": "SaaS",
                    "location": "USA",
                    "employee_count": {"min": 100, "max": 1000},
                    "revenue": {"min": 20000000, "max": 200000000}
                },
                "signals": ["recent_funding", "hiring_for_sales"],
                "limit": 5  # Limit to 5 results for testing
            }
        )
        
        print("\n   Executing search...")
        result = agent.execute(test_input)
        
        print(f"\n✅ Search completed")
        print(f"   Success: {result.success}")
        
        if not result.success:
            print(f"   Error: {result.error}")
            return False
        
        # Extract data from AgentOutput
        result_data = result.data
        leads = result_data.get('leads', [])
        
        print(f"   Total leads found: {len(leads)}")
        
        # Display sample leads
        if leads:
            print(f"\n📧 Sample Leads (showing first 3):")
            for i, lead in enumerate(leads[:3], 1):
                print(f"\n   Lead {i}:")
                print(f"      Company: {lead.get('company', 'N/A')}")
                print(f"      Contact: {lead.get('contact_name', 'N/A')}")
                print(f"      Title: {lead.get('title', 'N/A')}")
                print(f"      Email: {lead.get('email', 'N/A')}")
                print(f"      LinkedIn: {lead.get('linkedin', 'N/A')}")
                print(f"      Location: {lead.get('location', 'N/A')}")
                print(f"      Company Size: {lead.get('company_size', 'N/A')}")
                print(f"      Industry: {lead.get('industry', 'N/A')}")
                
                signals = lead.get('signals', [])
                if signals:
                    print(f"      Signals: {', '.join(signals)}")
        else:
            print("\n   No leads found matching the criteria")
            print("   This could mean:")
            print("      - The ICP criteria is too restrictive")
            print("      - Apollo API has no matching data")
            print("      - API rate limits reached")
        
        # Display search metadata
        metadata = result_data.get('search_metadata', {})
        if metadata:
            print(f"\n📊 Search Metadata:")
            print(f"   Total results: {metadata.get('total_results', 0)}")
            print(f"   Search time: {metadata.get('search_time', 'N/A')}")
            print(f"   API used: {metadata.get('api_source', 'N/A')}")
        
        # Test 2: Test with different criteria (smaller scope)
        print("\n\n📊 Test 2: Searching with broader criteria...")
        print("   Criteria: SaaS companies in USA (no size/revenue filters)")
        
        test_input_2 = AgentInput(
            agent_id="prospect_search",
            data={
                "icp": {
                    "industry": "SaaS",
                    "location": "USA"
                },
                "limit": 3
            }
        )
        
        result_2 = agent.execute(test_input_2)
        
        if result_2.success:
            leads_2 = result_2.data.get('leads', [])
            print(f"   ✅ Found {len(leads_2)} leads with broader criteria")
            
            if leads_2:
                print(f"\n   Sample lead:")
                sample = leads_2[0]
                print(f"      {sample.get('contact_name', 'N/A')} at {sample.get('company', 'N/A')}")
                print(f"      {sample.get('title', 'N/A')}")
        else:
            print(f"   ❌ Search failed: {result_2.error}")
        
        print("\n\n🎉 Prospect Search Agent tests completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_setup_instructions():
    """Show setup instructions for Prospect Search Agent."""
    print("\n" + "=" * 60)
    print("🔧 Prospect Search Agent Setup Instructions")
    print("=" * 60)
    
    print("\n1. Get Apollo API Key:")
    print("   - Sign up at https://www.apollo.io/")
    print("   - Go to Settings → Integrations → API")
    print("   - Copy your API key")
    
    print("\n2. Get Clay API Key (Optional):")
    print("   - Sign up at https://clay.com/")
    print("   - Get your API key from settings")
    
    print("\n3. Set Environment Variables:")
    print("   Add to your .env file:")
    print("   APOLLO_API_KEY='your_apollo_api_key_here'")
    print("   CLAY_API_KEY='your_clay_api_key_here'  # Optional")
    
    print("\n4. Run Test:")
    print("   python test_prospect_search.py")


def main():
    """Main function."""
    print("🚀 Prospect Search Agent Test")
    print("Testing prospect discovery with Apollo API")
    
    # Check if we have the required environment variables
    if not os.getenv('APOLLO_API_KEY'):
        print("\n⚠️  APOLLO_API_KEY environment variable not set")
        show_setup_instructions()
        return 1
    
    # Run the test
    success = test_prospect_search_agent()
    
    if not success:
        print("\n❌ Test failed. Check the setup instructions above.")
        return 1
    
    print("\n✅ Prospect Search Agent is working correctly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
