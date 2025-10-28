"""
DataEnrichmentAgent - Enriches lead data using external APIs.

This agent takes raw prospect data and enriches it with additional
information like company details, contact roles, and technology stack.
"""

import requests
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentInput
from .technology_enrichment import TechnologyEnrichment


class DataEnrichmentAgent(BaseAgent):
    """
    Agent responsible for enriching prospect data with additional information.
    
    Uses PeopleDataLabs API to add company details, contact roles,
    and technology stack information to leads.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the DataEnrichmentAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.peopledatalabs_api = None
        self.technology_enrichment = None
        self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> None:
        """Initialize API clients for data enrichment."""
        for tool_name, tool_instance in self._initialized_tools.items():
            if tool_name == "PeopleDataLabs":
                self.peopledatalabs_api = tool_instance
        
        # Initialize technology enrichment
        self.technology_enrichment = TechnologyEnrichment()
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """Create API client tools."""
        if tool_name == "PeopleDataLabs":
            return {
                "name": tool_name,
                "config": config,
                "session": requests.Session()
            }
        return super()._create_tool(tool_name, config)
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute data enrichment on the provided leads.
        
        Args:
            input_data: Contains leads to enrich
            
        Returns:
            Dictionary containing enriched leads
        """
        leads = input_data.data.get("leads", [])
        
        self.log_reasoning(
            "enrichment_start",
            f"Starting enrichment for {len(leads)} leads"
        )
        
        enriched_leads = []
        
        for i, lead in enumerate(leads):
            try:
                self.log_reasoning(
                    "enriching_lead",
                    f"Enriching lead {i+1}/{len(leads)}: {lead.get('company', 'Unknown')}"
                )
                
                enriched_lead = self._enrich_single_lead(lead)
                enriched_leads.append(enriched_lead)
                
            except Exception as e:
                self.log_reasoning(
                    "enrichment_error",
                    f"Failed to enrich lead {i+1}: {str(e)}"
                )
                # Add original lead with error flag
                enriched_leads.append({
                    **lead,
                    "enrichment_error": str(e),
                    "enriched": False
                })
        
        successful_enrichments = len([l for l in enriched_leads if l.get("enriched", True)])
        
        self.log_reasoning(
            "enrichment_complete",
            f"Enrichment completed: {successful_enrichments}/{len(leads)} successful",
            {"total_leads": len(leads), "successful": successful_enrichments}
        )
        
        return {
            "enriched_leads": enriched_leads,
            "enrichment_metadata": {
                "total_leads": len(leads),
                "successful_enrichments": successful_enrichments,
                "enrichment_timestamp": datetime.now().isoformat()
            }
        }
    
    def _enrich_single_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single lead with additional data.
        
        Args:
            lead: Lead data to enrich
            
        Returns:
            Enriched lead data
        """
        enriched_lead = lead.copy()
        enriched_lead["enriched"] = True
        
        # Enrich company data
        company_data = self._enrich_company_data(lead.get("company", ""))
        if company_data:
            enriched_lead.update(company_data)
        
        # Enrich technology data
        tech_data = self._enrich_technology_data(lead)
        if tech_data:
            enriched_lead.update(tech_data)
        
        # Enrich contact data using PeopleDataLabs
        contact_data = self._enrich_contact_data_pdl(lead)
        if contact_data:
            enriched_lead.update(contact_data)
        
        # Fallback to basic contact enrichment
        basic_contact_data = self._enrich_contact_data(lead)
        if basic_contact_data:
            enriched_lead.update(basic_contact_data)
        
        return enriched_lead
    
    def _enrich_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Enrich company data using PeopleDataLabs API.
        
        Args:
            company_name: Name of the company to enrich
            
        Returns:
            Dictionary with enriched company data
        """
        if not self.peopledatalabs_api or not company_name:
            return {}
        
        try:
            # Use PeopleDataLabs Company API
            response = self.peopledatalabs_api["session"].get(
                "https://api.peopledatalabs.com/v5/company/enrich",
                params={"name": company_name},
                headers={"X-Api-Key": self.peopledatalabs_api["config"]["api_key"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # PeopleDataLabs returns data directly, not nested under 'company'
                return {
                    "company_domain": data.get("website", ""),
                    "company_description": data.get("summary", ""),
                    "company_industry": data.get("industry", ""),
                    "company_size": data.get("employee_count", 0),
                    "company_revenue": data.get("annual_revenue", 0),
                    "company_location": data.get("location", {}).get("locality", ""),
                    "company_country": data.get("location", {}).get("country", ""),
                    "company_linkedin": data.get("linkedin_url", ""),
                    "company_twitter": data.get("twitter_url", ""),
                    "company_facebook": data.get("facebook_url", ""),
                    "company_crunchbase": data.get("crunchbase_url", ""),
                    "company_founded": data.get("founded", ""),
                    "company_type": data.get("type", ""),
                    "company_naics": data.get("naics", []),
                    "company_sic": data.get("sic", []),
                    "company_tags": data.get("tags", []),
                    "company_ticker": data.get("ticker", ""),
                    "company_headline": data.get("headline", ""),
                    "company_funding": data.get("total_funding_raised", 0),
                    "company_funding_stage": data.get("latest_funding_stage", ""),
                    "company_employee_count_by_country": data.get("employee_count_by_country", {}),
                    "company_alternative_names": data.get("alternative_names", []),
                    "company_alternative_domains": data.get("alternative_domains", []),
                    "company_industry_v2": data.get("industry_v2", ""),
                    "company_size_category": data.get("size", ""),
                    "company_linkedin_id": data.get("linkedin_id", ""),
                    "company_linkedin_slug": data.get("linkedin_slug", ""),
                    "company_mic_exchange": data.get("mic_exchange", ""),
                    "company_last_funding_date": data.get("last_funding_date", ""),
                    "company_number_funding_rounds": data.get("number_funding_rounds", 0),
                    "company_funding_stages": data.get("funding_stages", []),
                    "company_profiles": data.get("profiles", []),
                    "company_affiliated_profiles": data.get("affiliated_profiles", [])
                }
            else:
                self.log_reasoning(
                    "peopledatalabs_error",
                    f"PeopleDataLabs API error for {company_name}: {response.status_code}"
                )
                return {}
                
        except Exception as e:
            self.log_reasoning(
                "peopledatalabs_exception",
                f"PeopleDataLabs API exception for {company_name}: {str(e)}"
            )
            return {}
    
    def _enrich_technology_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich lead with technology stack data.
        
        Args:
            lead: Lead data containing company information
            
        Returns:
            Dictionary with technology enrichment data
        """
        if not self.technology_enrichment:
            return {}
        
        try:
            company_domain = lead.get("company_domain", "")
            company_name = lead.get("company", "")
            
            # If we don't have domain from PeopleDataLabs, try to construct it
            if not company_domain and company_name:
                # Simple domain construction (in real implementation, you'd use more sophisticated logic)
                company_domain = f"{company_name.lower().replace(' ', '')}.com"
            
            if not company_domain and not company_name:
                return {}
            
            self.log_reasoning(
                "tech_enrichment_start",
                f"Starting technology enrichment for {company_name} ({company_domain})"
            )
            
            # Get technology data
            tech_data = self.technology_enrichment.enrich_company_technologies(
                company_domain=company_domain,
                company_name=company_name
            )
            
            if tech_data.get("company_technologies"):
                self.log_reasoning(
                    "tech_enrichment_success",
                    f"Found {len(tech_data['company_technologies'])} technologies from {len(tech_data['company_tech_sources'])} sources"
                )
                
                # Add technology insights
                insights = self.technology_enrichment.get_technology_insights(
                    tech_data["company_technologies"]
                )
                tech_data.update(insights)
                
                return tech_data
            else:
                self.log_reasoning(
                    "tech_enrichment_no_data",
                    "No technology data found for this company"
                )
                return {}
                
        except Exception as e:
            self.log_reasoning(
                "tech_enrichment_error",
                f"Technology enrichment error: {str(e)}"
            )
            return {}
    
    def _enrich_contact_data_pdl(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich contact data using PeopleDataLabs Person API.
        
        Args:
            lead: Lead data containing contact information
            
        Returns:
            Dictionary with enriched contact data
        """
        if not self.peopledatalabs_api:
            return {}
        
        # Try to enrich using email if available
        email = lead.get("email", "")
        if not email or "@" not in email:
            return {}
        
        try:
            # Use PeopleDataLabs Person API
            response = self.peopledatalabs_api["session"].get(
                "https://api.peopledatalabs.com/v5/person/enrich",
                params={"email": email},
                headers={"X-Api-Key": self.peopledatalabs_api["config"]["api_key"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # PeopleDataLabs returns person data directly, not nested under 'person'
                return {
                    "contact_title": data.get("title", ""),
                    "contact_role": data.get("job_title", ""),
                    "contact_seniority": data.get("seniority", ""),
                    "contact_department": data.get("department", ""),
                    "contact_experience": data.get("experience", []),
                    "contact_education": data.get("education", []),
                    "contact_skills": data.get("skills", []),
                    "contact_languages": data.get("languages", []),
                    "contact_location": data.get("location", {}).get("locality", ""),
                    "contact_country": data.get("location", {}).get("country", ""),
                    "contact_linkedin": data.get("linkedin_url", ""),
                    "contact_twitter": data.get("twitter_url", ""),
                    "contact_facebook": data.get("facebook_url", ""),
                    "contact_github": data.get("github_url", ""),
                    "contact_phone": data.get("phone_numbers", [{}])[0].get("number", "") if data.get("phone_numbers") else "",
                    "contact_birth_year": data.get("birth_year", ""),
                    "contact_gender": data.get("gender", ""),
                    "contact_nationality": data.get("nationality", ""),
                    "contact_industry": data.get("industry", ""),
                    "contact_sub_industry": data.get("sub_industry", ""),
                    "contact_company_domain": data.get("company", {}).get("website", "") if data.get("company") else "",
                    "contact_company_name": data.get("company", {}).get("name", "") if data.get("company") else "",
                    "contact_company_size": data.get("company", {}).get("employee_count", 0) if data.get("company") else 0,
                    "contact_company_industry": data.get("company", {}).get("industry", "") if data.get("company") else "",
                    "contact_company_location": data.get("company", {}).get("location", {}).get("locality", "") if data.get("company", {}).get("location") else "",
                    "contact_company_country": data.get("company", {}).get("location", {}).get("country", "") if data.get("company", {}).get("location") else "",
                    "contact_company_linkedin": data.get("company", {}).get("linkedin_url", "") if data.get("company") else "",
                    "contact_company_twitter": data.get("company", {}).get("twitter_url", "") if data.get("company") else "",
                    "contact_company_facebook": data.get("company", {}).get("facebook_url", "") if data.get("company") else "",
                    "contact_company_crunchbase": data.get("company", {}).get("crunchbase_url", "") if data.get("company") else "",
                    "contact_company_founded": data.get("company", {}).get("founded", "") if data.get("company") else "",
                    "contact_company_type": data.get("company", {}).get("type", "") if data.get("company") else "",
                    "contact_company_naics": data.get("company", {}).get("naics", []) if data.get("company") else [],
                    "contact_company_sic": data.get("company", {}).get("sic", []) if data.get("company") else [],
                    "contact_company_tags": data.get("company", {}).get("tags", []) if data.get("company") else []
                }
            else:
                self.log_reasoning(
                    "peopledatalabs_person_error",
                    f"PeopleDataLabs Person API error for {email}: {response.status_code}"
                )
                return {}
                
        except Exception as e:
            self.log_reasoning(
                "peopledatalabs_person_exception",
                f"PeopleDataLabs Person API exception for {email}: {str(e)}"
            )
            return {}
    
    def _enrich_contact_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich contact data using available information.
        
        Args:
            lead: Lead data containing contact information
            
        Returns:
            Dictionary with enriched contact data
        """
        enriched_data = {}
        
        # Extract role from contact name or company context
        contact_name = lead.get("contact_name", "")
        if contact_name:
            # Simple role extraction based on common patterns
            role = self._extract_role_from_name(contact_name)
            if role:
                enriched_data["role"] = role
        
        # Add LinkedIn profile analysis if available
        linkedin_url = lead.get("linkedin", "")
        if linkedin_url:
            enriched_data["linkedin_profile"] = linkedin_url
            # Could add more sophisticated LinkedIn analysis here
        
        # Add email domain analysis
        email = lead.get("email", "")
        if email and "@" in email:
            domain = email.split("@")[1]
            enriched_data["email_domain"] = domain
            enriched_data["is_corporate_email"] = self._is_corporate_email(domain)
        
        return enriched_data
    
    def _extract_role_from_name(self, name: str) -> Optional[str]:
        """
        Extract role information from contact name.
        
        Args:
            name: Full name of the contact
            
        Returns:
            Extracted role or None
        """
        # Simple role extraction - could be enhanced with more sophisticated NLP
        name_lower = name.lower()
        
        role_keywords = {
            "ceo": ["ceo", "chief executive"],
            "cto": ["cto", "chief technology"],
            "vp_sales": ["vp sales", "vice president sales"],
            "vp_marketing": ["vp marketing", "vice president marketing"],
            "sales_director": ["sales director", "director of sales"],
            "marketing_director": ["marketing director", "director of marketing"],
            "founder": ["founder", "co-founder"],
            "president": ["president"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return role
        
        return None
    
    def _is_corporate_email(self, domain: str) -> bool:
        """
        Check if email domain appears to be corporate (not personal).
        
        Args:
            domain: Email domain to check
            
        Returns:
            True if domain appears corporate
        """
        personal_domains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "aol.com", "icloud.com", "protonmail.com"
        }
        
        return domain.lower() not in personal_domains
