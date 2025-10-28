#!/usr/bin/env python3
"""
Test script for ResponseTrackerAgent.

This script tests the response tracking functionality using Apollo API
to monitor campaign engagement metrics.
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

from agents.response_tracker_agent import ResponseTrackerAgent
from agents.base_agent import AgentInput


def test_response_tracker_agent():
    """Test Response Tracker Agent functionality."""
    print("🧪 Testing Response Tracker Agent")
    print("=" * 60)
    
    # Check environment variables
    apollo_api_key = os.getenv('APOLLO_API_KEY')
    apollo_campaign_id = os.getenv('APOLLO_CAMPAIGN_ID', 'test_campaign_001')
    
    if not apollo_api_key:
        print("❌ APOLLO_API_KEY environment variable not set")
        print("   Set it in your .env file to test Apollo API integration")
        return False
    
    print(f"✅ Apollo API Key: {apollo_api_key[:10]}...{apollo_api_key[-4:]}")
    print(f"✅ Campaign ID: {apollo_campaign_id}")
    
    try:
        # Initialize Response Tracker Agent
        print("\n🔧 Initializing Response Tracker Agent...")
        
        agent = ResponseTrackerAgent(
            agent_id="response_tracker",
            instructions="Monitor email responses and engagement using Apollo API",
            tools=[
                {
                    "name": "ApolloAPI",
                    "config": {
                        "api_key": apollo_api_key,
                        "endpoint": "https://api.apollo.io/v1"
                    }
                }
            ]
        )
        
        print("✅ Response Tracker Agent initialized successfully")
        
        # Test 1: Track responses with campaign ID from .env
        print("\n📊 Test 1: Tracking responses for a campaign...")
        print(f"   Using campaign ID: {apollo_campaign_id}")
        
        test_input = AgentInput(
            agent_id="response_tracker",
            data={
                "campaign_id": apollo_campaign_id
            }
        )
        
        result = agent.execute(test_input)
        
        print(f"\n✅ Tracking completed")
        print(f"   Success: {result.success}")
        
        # Extract data from AgentOutput
        result_data = result.data
        responses = result_data.get('responses', [])
        
        print(f"   Total responses: {len(responses)}")
        
        # Display engagement metrics
        metrics = result_data.get("engagement_metrics", {})
        print(f"\n📈 Engagement Metrics:")
        print(f"   Total activities: {metrics.get('total_activities', 0)}")
        print(f"   Emails sent: {metrics.get('emails_sent', 0)}")
        print(f"   Emails opened: {metrics.get('emails_opened', 0)}")
        print(f"   Emails clicked: {metrics.get('emails_clicked', 0)}")
        print(f"   Emails replied: {metrics.get('emails_replied', 0)}")
        print(f"   Open rate: {metrics.get('open_rate', 0)}%")
        print(f"   Click rate: {metrics.get('click_rate', 0)}%")
        print(f"   Reply rate: {metrics.get('reply_rate', 0)}%")
        
        # Display sample responses
        if responses:
            print(f"\n📧 Sample Responses (showing first 3):")
            for i, response in enumerate(responses[:3], 1):
                print(f"\n   Response {i}:")
                print(f"      Contact: {response.get('contact_name', 'N/A')} ({response.get('contact_email', 'N/A')})")
                print(f"      Activity Type: {response.get('activity_type', 'N/A')}")
                print(f"      Status: {response.get('status', 'N/A')}")
                print(f"      Timestamp: {response.get('timestamp', 'N/A')}")
                metadata = response.get('metadata', {})
                print(f"      Opened: {metadata.get('opened', False)}")
                print(f"      Clicked: {metadata.get('clicked', False)}")
                print(f"      Replied: {metadata.get('replied', False)}")
        else:
            print("\n   No responses found for this campaign ID")
            print("   This is expected if:")
            print("      - The campaign ID doesn't exist")
            print("      - The campaign has no activities yet")
            print("      - You're using a test/demo API key")
        
        # Test 2: Test with Apollo API directly to verify connectivity
        print("\n\n📡 Test 2: Verifying Apollo API connectivity...")
        print("   Testing Apollo API endpoint...")
        
        import requests
        
        # Test Apollo API with a simple request
        test_response = requests.get(
            "https://api.apollo.io/v1/auth/health",
            headers={
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "X-Api-Key": apollo_api_key
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✅ Apollo API connection successful")
            print(f"   Status: {test_response.status_code}")
        else:
            print(f"⚠️  Apollo API returned status: {test_response.status_code}")
            print(f"   Response: {test_response.text[:200]}")
        
        # Test 3: List available sequences (if any)
        print("\n\n📋 Test 3: Listing available sequences...")
        
        sequences_response = requests.post(
            "https://api.apollo.io/v1/emailer_campaigns/search",
            headers={
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "X-Api-Key": apollo_api_key
            },
            json={
                "per_page": 5
            },
            timeout=10
        )
        
        if sequences_response.status_code == 200:
            sequences_data = sequences_response.json()
            campaigns = sequences_data.get("emailer_campaigns", [])
            
            if campaigns:
                print(f"✅ Found {len(campaigns)} campaign(s)")
                print("\n   Available campaigns:")
                for i, campaign in enumerate(campaigns[:5], 1):
                    print(f"\n   Campaign {i}:")
                    print(f"      ID: {campaign.get('id', 'N/A')}")
                    print(f"      Name: {campaign.get('name', 'N/A')}")
                    print(f"      Status: {campaign.get('active', 'N/A')}")
                    print(f"      Created: {campaign.get('created_at', 'N/A')}")
                
                print("\n💡 Tip: Use one of these campaign IDs to test response tracking")
            else:
                print("   No campaigns found in your Apollo account")
        else:
            print(f"⚠️  Could not fetch campaigns: {sequences_response.status_code}")
            print(f"   Response: {sequences_response.text[:200]}")
        
        print("\n\n🎉 Response Tracker Agent tests completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_setup_instructions():
    """Show setup instructions for Response Tracker Agent."""
    print("\n" + "=" * 60)
    print("🔧 Response Tracker Agent Setup Instructions")
    print("=" * 60)
    
    print("\n1. Get Apollo API Key:")
    print("   - Sign up at https://www.apollo.io/")
    print("   - Go to Settings → Integrations → API")
    print("   - Copy your API key")
    
    print("\n2. Set Environment Variables:")
    print("   Add to your .env file:")
    print("   APOLLO_API_KEY='your_apollo_api_key_here'")
    print("   APOLLO_CAMPAIGN_ID='your_campaign_sequence_id_here'")
    
    print("\n3. Create a Campaign:")
    print("   - Create an email sequence in Apollo")
    print("   - Copy the sequence/campaign ID")
    print("   - Add it to APOLLO_CAMPAIGN_ID in your .env file")
    
    print("\n4. Run Test:")
    print("   python test_response_tracker.py")


def main():
    """Main function."""
    print("🚀 Response Tracker Agent Test")
    print("Testing campaign response tracking with Apollo API")
    
    # Check if we have the required environment variables
    if not os.getenv('APOLLO_API_KEY'):
        print("\n⚠️  APOLLO_API_KEY environment variable not set")
        show_setup_instructions()
        return 1
    
    # Run the test
    success = test_response_tracker_agent()
    
    if not success:
        print("\n❌ Test failed. Check the setup instructions above.")
        return 1
    
    print("\n✅ Response Tracker Agent is working correctly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
