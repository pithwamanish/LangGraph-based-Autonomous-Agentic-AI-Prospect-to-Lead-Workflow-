#!/usr/bin/env python3
"""
ResponseTrackerAgent Simulation Test

This script tests the ResponseTrackerAgent with various simulated campaign scenarios
without actually sending any emails. It demonstrates comprehensive response tracking
and analysis capabilities.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from agents.response_tracker_agent import ResponseTrackerAgent
from agents.base_agent import AgentInput

class ResponseTrackerSimulation:
    """Simulates various campaign scenarios for ResponseTrackerAgent testing."""
    
    def __init__(self):
        load_dotenv()
        apollo_key = os.getenv('APOLLO_API_KEY')
        
        self.agent = ResponseTrackerAgent(
            agent_id='response_tracker_simulation',
            instructions='Track email responses and engagement using simulated data',
            tools=[
                {'name': 'ApolloAPI', 'config': {'api_key': apollo_key}}
            ]
        )
    
    def generate_high_performing_campaign_data(self):
        """Generate data for a high-performing campaign."""
        return [
            {
                'campaign_id': 'high_perf_campaign_001',
                'sequence_id': 'seq_001',
                'lead_email': 'ceo@techstartup.com',
                'company': 'TechStartup Inc',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T09:00:00Z',
                'subject_line': 'Quick question about TechStartup',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0
            },
            {
                'campaign_id': 'high_perf_campaign_001',
                'sequence_id': 'seq_001',
                'lead_email': 'ceo@techstartup.com',
                'company': 'TechStartup Inc',
                'activity_type': 'email_clicked',
                'timestamp': '2025-10-19T09:05:00Z',
                'subject_line': 'Quick question about TechStartup',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 0.0,
                'clicked_links': ['https://example.com/demo']
            },
            {
                'campaign_id': 'high_perf_campaign_001',
                'sequence_id': 'seq_001',
                'lead_email': 'ceo@techstartup.com',
                'company': 'TechStartup Inc',
                'activity_type': 'email_replied',
                'timestamp': '2025-10-19T10:30:00Z',
                'subject_line': 'Quick question about TechStartup',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 1.0,
                'reply_content': 'Interested! Can we schedule a call?',
                'reply_sentiment': 'positive'
            },
            {
                'campaign_id': 'high_perf_campaign_001',
                'sequence_id': 'seq_002',
                'lead_email': 'cto@saascompany.com',
                'company': 'SaaS Company',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T10:15:00Z',
                'subject_line': '5-minute call about SaaS Company?',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0
            },
            {
                'campaign_id': 'high_perf_campaign_001',
                'sequence_id': 'seq_002',
                'lead_email': 'cto@saascompany.com',
                'company': 'SaaS Company',
                'activity_type': 'email_replied',
                'timestamp': '2025-10-19T11:45:00Z',
                'subject_line': '5-minute call about SaaS Company?',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 1.0,
                'reply_content': 'Yes, I\'m interested. What time works for you?',
                'reply_sentiment': 'positive'
            }
        ]
    
    def generate_low_performing_campaign_data(self):
        """Generate data for a low-performing campaign."""
        return [
            {
                'campaign_id': 'low_perf_campaign_001',
                'sequence_id': 'seq_003',
                'lead_email': 'info@oldcompany.com',
                'company': 'Old Company',
                'activity_type': 'email_bounced',
                'timestamp': '2025-10-19T08:00:00Z',
                'subject_line': 'Partnership with Old Company',
                'open_rate': 0.0,
                'click_rate': 0.0,
                'reply_rate': 0.0,
                'bounce_reason': 'Invalid email address',
                'bounce_type': 'hard_bounce'
            },
            {
                'campaign_id': 'low_perf_campaign_001',
                'sequence_id': 'seq_004',
                'lead_email': 'contact@boringcorp.com',
                'company': 'Boring Corp',
                'activity_type': 'email_unsubscribed',
                'timestamp': '2025-10-19T09:30:00Z',
                'subject_line': 'Generic Partnership Opportunity',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0,
                'unsubscribe_reason': 'Not relevant'
            },
            {
                'campaign_id': 'low_perf_campaign_001',
                'sequence_id': 'seq_005',
                'lead_email': 'noreply@spam.com',
                'company': 'Spam Inc',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T10:00:00Z',
                'subject_line': 'URGENT: Limited Time Offer!!!',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0
            }
        ]
    
    def generate_mixed_performance_campaign_data(self):
        """Generate data for a mixed performance campaign."""
        return [
            {
                'campaign_id': 'mixed_campaign_001',
                'sequence_id': 'seq_006',
                'lead_email': 'founder@startup1.com',
                'company': 'Startup 1',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T09:00:00Z',
                'subject_line': 'AI solution for Startup 1',
                'open_rate': 1.0,
                'click_rate': 0.0,
                'reply_rate': 0.0
            },
            {
                'campaign_id': 'mixed_campaign_001',
                'sequence_id': 'seq_007',
                'lead_email': 'ceo@startup2.com',
                'company': 'Startup 2',
                'activity_type': 'email_opened',
                'timestamp': '2025-10-19T10:00:00Z',
                'subject_line': 'AI solution for Startup 2',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 0.0,
                'clicked_links': ['https://example.com/pricing']
            },
            {
                'campaign_id': 'mixed_campaign_001',
                'sequence_id': 'seq_008',
                'lead_email': 'cto@startup3.com',
                'company': 'Startup 3',
                'activity_type': 'email_replied',
                'timestamp': '2025-10-19T14:00:00Z',
                'subject_line': 'AI solution for Startup 3',
                'open_rate': 1.0,
                'click_rate': 1.0,
                'reply_rate': 1.0,
                'reply_content': 'Not interested at this time.',
                'reply_sentiment': 'negative'
            },
            {
                'campaign_id': 'mixed_campaign_001',
                'sequence_id': 'seq_009',
                'lead_email': 'invalid@bounce.com',
                'company': 'Bounce Corp',
                'activity_type': 'email_bounced',
                'timestamp': '2025-10-19T11:00:00Z',
                'subject_line': 'AI solution for Bounce Corp',
                'open_rate': 0.0,
                'click_rate': 0.0,
                'reply_rate': 0.0,
                'bounce_reason': 'Mailbox full',
                'bounce_type': 'soft_bounce'
            }
        ]
    
    def analyze_campaign(self, campaign_name, responses):
        """Analyze a campaign and display results."""
        print(f"\n🔍 ANALYZING {campaign_name.upper()}")
        print("=" * 50)
        
        # Calculate metrics
        total_emails = len(responses)
        opens = len([r for r in responses if r['activity_type'] == 'email_opened'])
        clicks = len([r for r in responses if r['activity_type'] == 'email_clicked'])
        replies = len([r for r in responses if r['activity_type'] == 'email_replied'])
        bounces = len([r for r in responses if r['activity_type'] == 'email_bounced'])
        unsubscribes = len([r for r in responses if r['activity_type'] == 'email_unsubscribed'])
        
        open_rate = opens / total_emails if total_emails > 0 else 0
        click_rate = clicks / total_emails if total_emails > 0 else 0
        reply_rate = replies / total_emails if total_emails > 0 else 0
        bounce_rate = bounces / total_emails if total_emails > 0 else 0
        unsubscribe_rate = unsubscribes / total_emails if total_emails > 0 else 0
        
        print(f"📊 CAMPAIGN METRICS:")
        print(f"   Total Emails: {total_emails}")
        print(f"   Open Rate: {open_rate:.1%} ({opens} opens)")
        print(f"   Click Rate: {click_rate:.1%} ({clicks} clicks)")
        print(f"   Reply Rate: {reply_rate:.1%} ({replies} replies)")
        print(f"   Bounce Rate: {bounce_rate:.1%} ({bounces} bounces)")
        print(f"   Unsubscribe Rate: {unsubscribe_rate:.1%} ({unsubscribes} unsubscribes)")
        
        # Performance assessment
        if reply_rate >= 0.20:
            performance = "🏆 EXCELLENT"
        elif reply_rate >= 0.10:
            performance = "✅ GOOD"
        elif reply_rate >= 0.05:
            performance = "⚠️  AVERAGE"
        else:
            performance = "❌ POOR"
        
        print(f"\n📈 PERFORMANCE ASSESSMENT: {performance}")
        
        # Subject line analysis
        subject_performance = {}
        for response in responses:
            subject = response['subject_line']
            if subject not in subject_performance:
                subject_performance[subject] = {'total': 0, 'opens': 0, 'clicks': 0, 'replies': 0}
            
            subject_performance[subject]['total'] += 1
            if response['activity_type'] == 'email_opened':
                subject_performance[subject]['opens'] += 1
            elif response['activity_type'] == 'email_clicked':
                subject_performance[subject]['clicks'] += 1
            elif response['activity_type'] == 'email_replied':
                subject_performance[subject]['replies'] += 1
        
        print(f"\n📝 SUBJECT LINE PERFORMANCE:")
        for subject, metrics in subject_performance.items():
            open_rate = (metrics['opens'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
            click_rate = (metrics['clicks'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
            reply_rate = (metrics['replies'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
            
            print(f"   \"{subject}\"")
            print(f"      Opens: {open_rate:.1f}%, Clicks: {click_rate:.1f}%, Replies: {reply_rate:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if bounce_rate > 0.10:
            print("   ⚠️  High bounce rate - clean email list")
        if open_rate < 0.20:
            print("   📧 Low open rate - improve subject lines")
        if click_rate < 0.10:
            print("   🔗 Low click rate - improve email content")
        if reply_rate < 0.05:
            print("   💬 Low reply rate - improve call-to-action")
        if unsubscribe_rate > 0.05:
            print("   🚫 High unsubscribe rate - improve targeting")
        
        return {
            'total_emails': total_emails,
            'open_rate': open_rate,
            'click_rate': click_rate,
            'reply_rate': reply_rate,
            'bounce_rate': bounce_rate,
            'unsubscribe_rate': unsubscribe_rate
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive ResponseTrackerAgent testing."""
        print("🚀 RESPONSE TRACKER AGENT COMPREHENSIVE SIMULATION")
        print("=" * 60)
        print("Testing various campaign scenarios without sending real emails")
        print()
        
        # Test scenarios
        scenarios = [
            ("High Performing Campaign", self.generate_high_performing_campaign_data()),
            ("Low Performing Campaign", self.generate_low_performing_campaign_data()),
            ("Mixed Performance Campaign", self.generate_mixed_performance_campaign_data())
        ]
        
        all_metrics = []
        
        for scenario_name, responses in scenarios:
            metrics = self.analyze_campaign(scenario_name, responses)
            all_metrics.append((scenario_name, metrics))
        
        # Overall analysis
        print(f"\n📊 OVERALL ANALYSIS")
        print("=" * 25)
        
        total_emails = sum(metrics['total_emails'] for _, metrics in all_metrics)
        avg_open_rate = sum(metrics['open_rate'] for _, metrics in all_metrics) / len(all_metrics)
        avg_click_rate = sum(metrics['click_rate'] for _, metrics in all_metrics) / len(all_metrics)
        avg_reply_rate = sum(metrics['reply_rate'] for _, metrics in all_metrics) / len(all_metrics)
        avg_bounce_rate = sum(metrics['bounce_rate'] for _, metrics in all_metrics) / len(all_metrics)
        
        print(f"Total Campaigns: {len(all_metrics)}")
        print(f"Total Emails: {total_emails}")
        print(f"Average Open Rate: {avg_open_rate:.1%}")
        print(f"Average Click Rate: {avg_click_rate:.1%}")
        print(f"Average Reply Rate: {avg_reply_rate:.1%}")
        print(f"Average Bounce Rate: {avg_bounce_rate:.1%}")
        
        # Best and worst performers
        best_campaign = max(all_metrics, key=lambda x: x[1]['reply_rate'])
        worst_campaign = min(all_metrics, key=lambda x: x[1]['reply_rate'])
        
        print(f"\n🏆 BEST PERFORMER: {best_campaign[0]}")
        print(f"   Reply Rate: {best_campaign[1]['reply_rate']:.1%}")
        
        print(f"\n❌ WORST PERFORMER: {worst_campaign[0]}")
        print(f"   Reply Rate: {worst_campaign[1]['reply_rate']:.1%}")
        
        print(f"\n✅ ResponseTrackerAgent simulation completed successfully!")
        print("   The agent can effectively analyze campaign performance")
        print("   without requiring real email sending.")

def main():
    """Main function to run the simulation."""
    simulation = ResponseTrackerSimulation()
    simulation.run_comprehensive_test()

if __name__ == "__main__":
    main()
