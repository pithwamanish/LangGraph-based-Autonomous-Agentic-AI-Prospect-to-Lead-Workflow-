#!/usr/bin/env python3
"""
Email Monitor - Simple dashboard to view sent emails and responses.

This script provides a simple interface to monitor email campaigns
and track responses from the prospect-to-lead workflow.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

class EmailMonitor:
    """Simple email monitoring dashboard."""
    
    def __init__(self):
        load_dotenv()
        self.apollo_key = os.getenv('APOLLO_API_KEY')
        self.headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.apollo_key
        }
    
    def get_campaigns(self):
        """Get all email campaigns from Apollo."""
        try:
            response = requests.get(
                'https://api.apollo.io/v1/sequences',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                campaigns = data.get('emailer_campaigns', [])
                return campaigns
            else:
                print(f"❌ Error fetching campaigns: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def get_campaign_details(self, campaign_id):
        """Get detailed information about a specific campaign."""
        try:
            response = requests.get(
                f'https://api.apollo.io/v1/sequences/{campaign_id}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error fetching campaign details: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def display_campaigns(self):
        """Display all campaigns in a simple format."""
        print("🔍 EMAIL CAMPAIGNS MONITOR")
        print("=" * 50)
        
        campaigns = self.get_campaigns()
        
        if not campaigns:
            print("📭 No campaigns found")
            return
        
        print(f"📊 Found {len(campaigns)} campaigns:")
        print()
        
        for i, campaign in enumerate(campaigns, 1):
            campaign_id = campaign.get('id', 'N/A')
            name = campaign.get('name', 'Unnamed Campaign')
            created_at = campaign.get('created_at', 'N/A')
            archived = campaign.get('archived', False)
            
            print(f"📧 Campaign #{i}: {name}")
            print(f"   ID: {campaign_id}")
            print(f"   Created: {created_at}")
            print(f"   Status: {'Archived' if archived else 'Active'}")
            print()
    
    def display_campaign_details(self, campaign_id):
        """Display detailed information about a specific campaign."""
        print(f"🔍 CAMPAIGN DETAILS: {campaign_id}")
        print("=" * 50)
        
        details = self.get_campaign_details(campaign_id)
        
        if not details:
            print("❌ Could not fetch campaign details")
            return
        
        campaign = details.get('emailer_campaign', {})
        
        print(f"📧 Campaign Name: {campaign.get('name', 'N/A')}")
        print(f"🆔 Campaign ID: {campaign.get('id', 'N/A')}")
        print(f"📅 Created: {campaign.get('created_at', 'N/A')}")
        print(f"📊 Status: {'Archived' if campaign.get('archived') else 'Active'}")
        print(f"👤 User ID: {campaign.get('user_id', 'N/A')}")
        print()
        
        # Show steps (email content)
        steps = campaign.get('steps', [])
        if steps:
            print("📝 EMAIL STEPS:")
            for i, step in enumerate(steps, 1):
                print(f"   Step {i}: {step.get('type', 'N/A')}")
                if step.get('subject'):
                    print(f"      Subject: {step['subject']}")
                if step.get('body'):
                    body_preview = step['body'][:100] + "..." if len(step['body']) > 100 else step['body']
                    print(f"      Body: {body_preview}")
                print()
        
        # Show contacts
        contacts = campaign.get('contacts', [])
        if contacts:
            print(f"👥 CONTACTS ({len(contacts)}):")
            for i, contact in enumerate(contacts, 1):
                print(f"   {i}. {contact.get('first_name', '')} {contact.get('last_name', '')}")
                print(f"      Email: {contact.get('email', 'N/A')}")
                print(f"      Status: {contact.get('status', 'N/A')}")
                print()
    
    def monitor_recent_campaigns(self, hours=24):
        """Monitor campaigns from the last N hours."""
        print(f"⏰ MONITORING CAMPAIGNS FROM LAST {hours} HOURS")
        print("=" * 50)
        
        campaigns = self.get_campaigns()
        recent_campaigns = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for campaign in campaigns:
            created_at = campaign.get('created_at', '')
            if created_at:
                try:
                    # Parse ISO format datetime
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if created_dt.replace(tzinfo=None) > cutoff_time:
                        recent_campaigns.append(campaign)
                except:
                    continue
        
        if not recent_campaigns:
            print(f"📭 No campaigns found in the last {hours} hours")
            return
        
        print(f"📊 Found {len(recent_campaigns)} recent campaigns:")
        print()
        
        for i, campaign in enumerate(recent_campaigns, 1):
            campaign_id = campaign.get('id', 'N/A')
            name = campaign.get('name', 'Unnamed Campaign')
            created_at = campaign.get('created_at', 'N/A')
            
            print(f"📧 Campaign #{i}: {name}")
            print(f"   ID: {campaign_id}")
            print(f"   Created: {created_at}")
            print(f"   🔗 View in Apollo: https://app.apollo.io/sequences/{campaign_id}")
            print()

def main():
    """Main function to run the email monitor."""
    monitor = EmailMonitor()
    
    print("🚀 EMAIL MONITOR DASHBOARD")
    print("=" * 30)
    print()
    
    while True:
        print("Choose an option:")
        print("1. View all campaigns")
        print("2. View recent campaigns (last 24 hours)")
        print("3. View campaign details")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            monitor.display_campaigns()
        elif choice == '2':
            monitor.monitor_recent_campaigns()
        elif choice == '3':
            campaign_id = input("Enter campaign ID: ").strip()
            if campaign_id:
                monitor.display_campaign_details(campaign_id)
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
