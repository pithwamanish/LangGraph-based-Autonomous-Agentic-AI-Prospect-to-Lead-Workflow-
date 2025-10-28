#!/usr/bin/env python3
"""
Test script for Google Sheets integration in FeedbackTrainerAgent.

This script demonstrates how the Google Sheets integration works
with the FeedbackTrainerAgent.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.google_sheets_client import GoogleSheetsClient


def test_google_sheets_integration():
    """Test Google Sheets integration functionality."""
    print("🧪 Testing Google Sheets Integration")
    print("=" * 50)
    
    # Check environment variables
    sheet_id = os.getenv('SHEET_ID')
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    
    if not sheet_id:
        print("❌ SHEET_ID environment variable not set")
        print("   Set it to your Google Sheet ID")
        return False
    
    if not credentials_file:
        print("❌ GOOGLE_CREDENTIALS_FILE environment variable not set")
        print("   Set it to the path of your Google credentials JSON file")
        return False
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        return False
    
    print(f"✅ Sheet ID: {sheet_id}")
    print(f"✅ Credentials file: {credentials_file}")
    
    try:
        # Initialize Google Sheets client
        print("\n🔧 Initializing Google Sheets client...")
        client = GoogleSheetsClient(
            sheet_id=sheet_id,
            credentials_file=credentials_file
        )
        print("✅ Google Sheets client initialized successfully")
        
        # Test sheet creation
        print("\n📊 Creating required sheets...")
        success = client.create_sheets_if_not_exist()
        if success:
            print("✅ Sheets created/verified successfully")
        else:
            print("❌ Failed to create sheets")
            return False
        
        # Test writing recommendations
        print("\n📝 Testing recommendations writing...")
        test_recommendations = [
            {
                "type": "subject_line_optimization",
                "priority": "high",
                "title": "Improve Subject Lines",
                "description": "Low open rate indicates subject lines need improvement",
                "suggestions": [
                    "Use more personalized subject lines",
                    "Add urgency or curiosity elements",
                    "Test different subject line formats"
                ],
                "expected_impact": "Increase open rates by 20-30%"
            },
            {
                "type": "icp_adjustment",
                "priority": "medium",
                "title": "Refine Ideal Customer Profile",
                "description": "Current ICP may not be well-targeted",
                "suggestions": [
                    "Narrow down company size criteria",
                    "Focus on specific industries with higher response rates"
                ],
                "expected_impact": "Increase response rates by 15-25%"
            }
        ]
        
        success = client.write_recommendations(test_recommendations)
        if success:
            print(f"✅ Successfully wrote {len(test_recommendations)} recommendations")
        else:
            print("❌ Failed to write recommendations")
            return False
        
        # Test writing performance metrics
        print("\n📈 Testing performance metrics writing...")
        test_metrics = {
            "engagement_insights": {
                "open_rate": 15.5,
                "click_rate": 3.2,
                "reply_rate": 2.1,
                "overall_performance": "average"
            },
            "response_patterns": {
                "total_activities": 150,
                "emails_sent": 100,
                "emails_opened": 15,
                "emails_clicked": 3
            },
            "timing_analysis": {
                "peak_response_times": ["Tuesday 10 AM", "Wednesday 2 PM"],
                "low_response_times": ["Monday 8 AM", "Friday 4 PM"]
            }
        }
        
        success = client.write_performance_metrics(test_metrics)
        if success:
            print("✅ Successfully wrote performance metrics")
        else:
            print("❌ Failed to write performance metrics")
            return False
        
        print("\n🎉 All Google Sheets integration tests passed!")
        print("\n📋 Check your Google Sheet to see the data:")
        print(f"   https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_setup_instructions():
    """Show setup instructions for Google Sheets integration."""
    print("\n" + "=" * 60)
    print("🔧 Google Sheets Setup Instructions")
    print("=" * 60)
    
    print("\n1. Create Google Cloud Project:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Create new project or select existing")
    print("   - Enable Google Sheets API")
    
    print("\n2. Create Credentials:")
    print("   - Go to APIs & Services → Credentials")
    print("   - Create Service Account (recommended) or OAuth2 client")
    print("   - Download JSON credentials file")
    
    print("\n3. Create Google Sheet:")
    print("   - Go to https://sheets.google.com/")
    print("   - Create new spreadsheet")
    print("   - Copy Sheet ID from URL")
    
    print("\n4. Set Environment Variables:")
    print("   export SHEET_ID='your_sheet_id_here'")
    print("   export GOOGLE_CREDENTIALS_FILE='path/to/credentials.json'")
    
    print("\n5. Install Dependencies:")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")
    
    print("\n6. Run Test:")
    print("   python test_google_sheets.py")


def main():
    """Main function."""
    print("🚀 Google Sheets Integration Test")
    print("Testing FeedbackTrainerAgent Google Sheets functionality")
    
    # Check if we have the required environment variables
    if not os.getenv('SHEET_ID') or not os.getenv('GOOGLE_CREDENTIALS_FILE'):
        print("\n⚠️  Environment variables not set")
        show_setup_instructions()
        return 1
    
    # Run the test
    success = test_google_sheets_integration()
    
    if not success:
        print("\n❌ Test failed. Check the setup instructions above.")
        return 1
    
    print("\n✅ Google Sheets integration is working correctly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
