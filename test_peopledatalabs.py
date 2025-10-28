#!/usr/bin/env python3
"""
Test script for PeopleDataLabs DataEnrichmentAgent integration.

This script tests the DataEnrichmentAgent with PeopleDataLabs API
to verify company and contact enrichment functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.data_enrichment_agent import DataEnrichmentAgent
from agents.base_agent import AgentInput

def test_peopledatalabs_integration():
    """Test PeopleDataLabs integration with DataEnrichmentAgent."""
    
    print("🔍 Testing PeopleDataLabs DataEnrichmentAgent Integration")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get PeopleDataLabs API key
    pdl_api_key = os.getenv('PEOPLEDATALABS_API_KEY', 'your_peopledatalabs_api_key_here')
    
    if pdl_api_key == 'your_peopledatalabs_api_key_here':
        print("❌ Please set PEOPLEDATALABS_API_KEY in your .env file")
        print("   Get your API key from: https://www.peopledatalabs.com/")
        return
    
    print(f"Using API Key: {pdl_api_key[:10]}...")
    print()
    
    # Create DataEnrichmentAgent with PeopleDataLabs
    agent = DataEnrichmentAgent(
        agent_id='pdl_test',
        instructions='Enrich lead data using PeopleDataLabs API',
        tools=[
            {'name': 'PeopleDataLabs', 'config': {'api_key': pdl_api_key}}
        ]
    )
    
    print("✅ DataEnrichmentAgent created with PeopleDataLabs")
    print()
    
    # Test data - sample leads to enrich
    test_leads = [
        {
            "company": "TechFlow Solutions",
            "contact_name": "Sarah Johnson",
            "email": "sarah.johnson@techflowsolutions.com",
            "linkedin": "https://linkedin.com/in/sarahjohnson1",
            "signal": "recent_funding",
            "source": "clay"
        },
        {
            "company": "DataSync Inc",
            "contact_name": "Michael Smith",
            "email": "michael.smith@datasync.com",
            "linkedin": "https://linkedin.com/in/michaelsmith2",
            "signal": "hiring_for_sales",
            "source": "clay"
        },
        {
            "company": "CloudVault Systems",
            "contact_name": "Jennifer Williams",
            "email": "jennifer.williams@cloudvault.com",
            "linkedin": "https://linkedin.com/in/jenniferwilliams3",
            "signal": "recent_funding",
            "source": "clay"
        }
    ]
    
    print(f"🔍 Testing enrichment for {len(test_leads)} leads:")
    for i, lead in enumerate(test_leads, 1):
        print(f"   {i}. {lead['company']} - {lead['contact_name']} ({lead['email']})")
    print()
    
    # Create input data
    input_data = AgentInput(data={'leads': test_leads})
    
    print("🚀 Starting enrichment process...")
    print()
    
    # Execute enrichment
    result = agent.execute(input_data)
    
    print("📊 Enrichment Results:")
    print(f"   Success: {result.success}")
    print(f"   Execution Time: {result.execution_time:.2f}s")
    print()
    
    if result.success:
        enriched_leads = result.data.get('enriched_leads', [])
        metadata = result.data.get('enrichment_metadata', {})
        
        print(f"✅ Enrichment completed successfully!")
        print(f"   Total Leads: {metadata.get('total_leads', 0)}")
        print(f"   Successful Enrichments: {metadata.get('successful_enrichments', 0)}")
        print(f"   Enrichment Timestamp: {metadata.get('enrichment_timestamp', 'N/A')}")
        print()
        
        # Show detailed results for each lead
        for i, lead in enumerate(enriched_leads, 1):
            print(f"📋 Lead #{i}: {lead.get('company', 'N/A')}")
            print(f"   Contact: {lead.get('contact_name', 'N/A')}")
            print(f"   Email: {lead.get('email', 'N/A')}")
            print(f"   Enriched: {lead.get('enriched', False)}")
            
            if lead.get('enrichment_error'):
                print(f"   ❌ Error: {lead['enrichment_error']}")
            else:
                # Show company enrichment data
                company_fields = [
                    'company_domain', 'company_description', 'company_industry',
                    'company_size', 'company_revenue', 'company_technologies',
                    'company_location', 'company_country', 'company_linkedin'
                ]
                
                print("   🏢 Company Data:")
                for field in company_fields:
                    value = lead.get(field)
                    if value:
                        if isinstance(value, list) and value:
                            print(f"      {field}: {', '.join(map(str, value[:3]))}{'...' if len(value) > 3 else ''}")
                        else:
                            print(f"      {field}: {value}")
                
                # Show contact enrichment data
                contact_fields = [
                    'contact_title', 'contact_role', 'contact_seniority',
                    'contact_department', 'contact_skills', 'contact_location',
                    'contact_linkedin', 'contact_phone'
                ]
                
                print("   👤 Contact Data:")
                for field in contact_fields:
                    value = lead.get(field)
                    if value:
                        if isinstance(value, list) and value:
                            print(f"      {field}: {', '.join(map(str, value[:3]))}{'...' if len(value) > 3 else ''}")
                        else:
                            print(f"      {field}: {value}")
            
            print()
        
        # Summary of enrichment quality
        enriched_count = len([l for l in enriched_leads if l.get('enriched', False)])
        with_company_data = len([l for l in enriched_leads if l.get('company_domain')])
        with_contact_data = len([l for l in enriched_leads if l.get('contact_title')])
        
        print("📈 Enrichment Quality Summary:")
        print(f"   Successfully Enriched: {enriched_count}/{len(enriched_leads)}")
        print(f"   With Company Data: {with_company_data}/{len(enriched_leads)}")
        print(f"   With Contact Data: {with_contact_data}/{len(enriched_leads)}")
        
        if enriched_count > 0:
            print("\\n✅ PeopleDataLabs integration is working!")
        else:
            print("\\n⚠️  No leads were successfully enriched")
            print("   This might be due to:")
            print("   - Invalid API key")
            print("   - API rate limits")
            print("   - Data not found in PeopleDataLabs database")
            print("   - Network connectivity issues")
    
    else:
        print(f"❌ Enrichment failed: {result.error}")
        print("\\n🔧 Troubleshooting:")
        print("   1. Check your PeopleDataLabs API key")
        print("   2. Verify API key has sufficient credits")
        print("   3. Check network connectivity")
        print("   4. Review API documentation: https://docs.peopledatalabs.com/")
    
    print("\\n🎉 PeopleDataLabs integration test completed!")

if __name__ == "__main__":
    test_peopledatalabs_integration()
