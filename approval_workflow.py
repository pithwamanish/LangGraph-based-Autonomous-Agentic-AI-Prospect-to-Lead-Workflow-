#!/usr/bin/env python3
"""
Approval Workflow - Simulates human approval and applies updates.

This script demonstrates how the FeedbackTrainerAgent recommendations
are reviewed, approved, and applied to improve future campaigns.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agents.feedback_trainer_agent import FeedbackTrainerAgent
from agents.base_agent import AgentInput

class ApprovalWorkflow:
    """Handles the approval workflow for FeedbackTrainerAgent recommendations."""
    
    def __init__(self):
        load_dotenv()
        self.sheet_id = os.getenv('SHEET_ID')
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        
        # Initialize FeedbackTrainerAgent
        self.feedback_agent = FeedbackTrainerAgent(
            agent_id='approval_workflow',
            instructions='Analyze campaign performance and generate recommendations',
            tools=[
                {
                    'name': 'GoogleSheets', 
                    'config': {
                        'sheet_id': self.sheet_id,
                        'credentials': self.credentials_file
                    }
                }
            ]
        )
    
    def simulate_campaign_analysis(self):
        """Simulate analyzing a campaign and generating recommendations."""
        print("🔍 SIMULATING CAMPAIGN ANALYSIS")
        print("=" * 40)
        
        # Simulate campaign performance data
        responses = [
            {
                'lead_email': 'ceo@techstartup.com',
                'company': 'TechStartup Inc',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T09:00:00Z',
                'sequence_id': '68f4f131a548a3000df9096e',
                'subject_line': 'Partnership Opportunity - TechStartup',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0
            },
            {
                'lead_email': 'cto@enterprise.com',
                'company': 'Enterprise Corp',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T10:30:00Z',
                'sequence_id': '68f4f132893083001997cd1c',
                'subject_line': 'AI Integration for Enterprise Corp',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 0.0
            },
            {
                'lead_email': 'founder@saas.com',
                'company': 'SaaS Solutions',
                'activity_type': 'email_replied',
                'timestamp': '2025-10-19T14:15:00Z',
                'sequence_id': '68f4f138db127c00117e3a21',
                'subject_line': 'SaaS Partnership Opportunity',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 1.0,
                'reply_content': 'Interested in learning more about your AI platform.'
            },
            {
                'lead_email': 'invalid@bounce.com',
                'company': 'Bounce Corp',
                'activity_type': 'email_bounced',
                'timestamp': '2025-10-19T11:00:00Z',
                'sequence_id': '68f4f139db127c00117e3a23',
                'subject_line': 'Partnership with Bounce Corp',
                'open_rate': 0.0,
                'click_rate': 0.0,
                'reply_rate': 0.0,
                'bounce_reason': 'Invalid email address'
            }
        ]
        
        engagement_metrics = {
            'total_emails_sent': 4,
            'total_opens': 3,
            'total_clicks': 2,
            'total_replies': 1,
            'total_bounces': 1,
            'overall_open_rate': 0.75,
            'overall_click_rate': 0.50,
            'overall_reply_rate': 0.25,
            'overall_bounce_rate': 0.25,
            'campaign_duration_days': 1,
            'best_performing_subject': 'SaaS Partnership Opportunity',
            'worst_performing_subject': 'Partnership with Bounce Corp'
        }
        
        print(f"📊 Campaign Performance:")
        print(f"   Emails Sent: {engagement_metrics['total_emails_sent']}")
        print(f"   Open Rate: {engagement_metrics['overall_open_rate']:.1%}")
        print(f"   Click Rate: {engagement_metrics['overall_click_rate']:.1%}")
        print(f"   Reply Rate: {engagement_metrics['overall_reply_rate']:.1%}")
        print(f"   Bounce Rate: {engagement_metrics['overall_bounce_rate']:.1%}")
        print()
        
        # Run feedback analysis
        input_data = AgentInput(data={
            'responses': responses,
            'engagement_metrics': engagement_metrics
        })
        
        result = self.feedback_agent.execute(input_data)
        
        if result.success:
            recommendations = result.data.get('recommendations', [])
            print(f"✅ Generated {len(recommendations)} recommendations")
            return recommendations
        else:
            print(f"❌ Analysis failed: {result.error}")
            return []
    
    def display_recommendations(self, recommendations):
        """Display recommendations for human review."""
        print("\n🎯 RECOMMENDATIONS FOR REVIEW")
        print("=" * 35)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.get('title', 'No title')}")
            print(f"   Type: {rec.get('type', 'Unknown')}")
            print(f"   Priority: {rec.get('priority', 'Medium')}")
            print(f"   Impact: {rec.get('expected_impact', 'Unknown')}")
            print(f"   Description: {rec.get('description', 'No description')}")
            
            # Show specific suggestions
            if rec.get('type') == 'subject_line_optimization':
                suggestions = rec.get('suggestions', [])
                if suggestions:
                    print(f"   Suggested Subject Lines:")
                    for j, suggestion in enumerate(suggestions, 1):
                        print(f"      {j}. {suggestion}")
            
            elif rec.get('type') == 'icp_adjustment':
                icp_suggestions = rec.get('icp_suggestions', {})
                if icp_suggestions:
                    print(f"   ICP Suggestions:")
                    for key, value in icp_suggestions.items():
                        print(f"      {key}: {value}")
    
    def simulate_human_approval(self, recommendations):
        """Simulate human approval process."""
        print("\n👤 HUMAN APPROVAL SIMULATION")
        print("=" * 35)
        
        approved_recommendations = []
        
        for i, rec in enumerate(recommendations, 1):
            rec_type = rec.get('type', 'unknown')
            priority = rec.get('priority', 'medium')
            
            # Simulate approval logic based on priority and type
            if priority == 'high' and rec_type in ['subject_line_optimization', 'icp_adjustment']:
                approved = True
                reason = "High priority and critical for performance"
            elif priority == 'medium' and rec_type in ['email_content_optimization', 'timing_optimization']:
                approved = True
                reason = "Medium priority, good for testing"
            else:
                approved = False
                reason = "Low priority or not critical at this time"
            
            status = "✅ APPROVED" if approved else "❌ REJECTED"
            print(f"{i}. {rec.get('title', 'No title')} - {status}")
            print(f"   Reason: {reason}")
            
            if approved:
                approved_recommendations.append(rec)
        
        print(f"\n📊 Approval Summary:")
        print(f"   Total Recommendations: {len(recommendations)}")
        print(f"   Approved: {len(approved_recommendations)}")
        print(f"   Rejected: {len(recommendations) - len(approved_recommendations)}")
        
        return approved_recommendations
    
    def apply_approved_recommendations(self, approved_recommendations):
        """Apply approved recommendations to improve campaigns."""
        print("\n🔄 APPLYING APPROVED RECOMMENDATIONS")
        print("=" * 40)
        
        if not approved_recommendations:
            print("No recommendations to apply.")
            return
        
        applied_changes = []
        
        for rec in approved_recommendations:
            rec_type = rec.get('type', 'unknown')
            title = rec.get('title', 'No title')
            
            print(f"\n🔧 Applying: {title}")
            
            if rec_type == 'subject_line_optimization':
                # Apply subject line improvements
                new_subjects = [
                    "Quick question about {company_name}",
                    "Partnership opportunity - {company_name}",
                    "AI solution for {company_name}",
                    "5-minute call about {company_name}?"
                ]
                print(f"   ✅ Updated subject line templates")
                print(f"   📝 New templates: {len(new_subjects)} variations")
                applied_changes.append({
                    'type': 'subject_lines',
                    'changes': new_subjects,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif rec_type == 'icp_adjustment':
                # Apply ICP refinements
                icp_updates = {
                    'company_size': '50-500 employees (was 100-1000)',
                    'industry_focus': 'SaaS, Technology, E-commerce',
                    'funding_stage': 'Series A to Series C',
                    'technology_stack': 'Modern tech stack required'
                }
                print(f"   ✅ Refined ICP criteria")
                for key, value in icp_updates.items():
                    print(f"      {key}: {value}")
                applied_changes.append({
                    'type': 'icp_criteria',
                    'changes': icp_updates,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif rec_type == 'email_content_optimization':
                # Apply content improvements
                content_updates = {
                    'personalization': 'Enhanced with company-specific details',
                    'call_to_action': 'Clearer and more compelling',
                    'value_proposition': 'More specific and quantifiable',
                    'follow_up_sequence': 'Added 3-step follow-up sequence'
                }
                print(f"   ✅ Improved email content")
                for key, value in content_updates.items():
                    print(f"      {key}: {value}")
                applied_changes.append({
                    'type': 'email_content',
                    'changes': content_updates,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif rec_type == 'timing_optimization':
                # Apply timing improvements
                timing_updates = {
                    'send_time': 'Tuesday-Thursday, 10AM-2PM',
                    'follow_up_delay': '3 days (was 1 day)',
                    'sequence_length': '5 emails (was 3)',
                    'timezone_optimization': 'Recipient timezone-based sending'
                }
                print(f"   ✅ Optimized timing")
                for key, value in timing_updates.items():
                    print(f"      {key}: {value}")
                applied_changes.append({
                    'type': 'timing',
                    'changes': timing_updates,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Save applied changes
        self.save_applied_changes(applied_changes)
        
        print(f"\n✅ Successfully applied {len(applied_changes)} recommendation types")
        print(f"📊 Changes saved to configuration")
        
        return applied_changes
    
    def save_applied_changes(self, changes):
        """Save applied changes to a configuration file."""
        config_file = 'applied_recommendations.json'
        
        config = {
            'last_updated': datetime.now().isoformat(),
            'applied_changes': changes,
            'total_changes': len(changes)
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"💾 Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {str(e)}")
    
    def run_complete_workflow(self):
        """Run the complete approval workflow."""
        print("🚀 FEEDBACK TRAINER APPROVAL WORKFLOW")
        print("=" * 45)
        print("This demonstrates the complete process:")
        print("1. Analyze campaign performance")
        print("2. Generate recommendations")
        print("3. Human review and approval")
        print("4. Apply approved changes")
        print()
        
        # Step 1: Analyze campaign
        recommendations = self.simulate_campaign_analysis()
        
        if not recommendations:
            print("❌ No recommendations generated. Exiting.")
            return
        
        # Step 2: Display for review
        self.display_recommendations(recommendations)
        
        # Step 3: Simulate human approval
        approved_recommendations = self.simulate_human_approval(recommendations)
        
        # Step 4: Apply approved changes
        if approved_recommendations:
            applied_changes = self.apply_approved_recommendations(approved_recommendations)
            
            print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 40)
            print("✅ Campaign performance analyzed")
            print("✅ Recommendations generated and reviewed")
            print("✅ Human approval process completed")
            print("✅ Approved changes applied to configuration")
            print("✅ System ready for improved campaigns")
        else:
            print("\n⚠️  No recommendations were approved.")
            print("No changes will be applied to the system.")

def main():
    """Main function to run the approval workflow."""
    workflow = ApprovalWorkflow()
    workflow.run_complete_workflow()

if __name__ == "__main__":
    main()
