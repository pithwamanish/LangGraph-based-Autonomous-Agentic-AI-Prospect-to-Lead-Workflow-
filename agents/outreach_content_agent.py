"""
OutreachContentAgent - Generates personalized outreach messages.

This agent creates personalized email content for each lead based on
their profile, company information, and outreach persona.
"""

import json
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentInput


class OutreachContentAgent(BaseAgent):
    """
    Agent responsible for generating personalized outreach content.
    
    Uses OpenAI's GPT models to create personalized email messages
    based on lead data and outreach persona configuration.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the OutreachContentAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.openai_client = None
        self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> None:
        """Initialize API clients for content generation."""
        for tool_name, tool_instance in self._initialized_tools.items():
            if tool_name == "OpenAI":
                self.openai_client = tool_instance
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """Create API client tools."""
        if tool_name == "OpenAI":
            return {
                "name": tool_name,
                "config": config,
                "session": requests.Session()
            }
        return super()._create_tool(tool_name, config)
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute content generation for ranked leads.
        
        Args:
            input_data: Contains ranked leads and persona configuration
            
        Returns:
            Dictionary containing generated messages
        """
        ranked_leads = input_data.data.get("ranked_leads", [])
        persona = input_data.data.get("persona", "SDR")
        tone = input_data.data.get("tone", "friendly")
        
        self.log_reasoning(
            "content_generation_start",
            f"Generating content for {len(ranked_leads)} leads with persona: {persona}, tone: {tone}"
        )
        
        messages = []
        
        for i, lead in enumerate(ranked_leads):
            try:
                self.log_reasoning(
                    "generating_content",
                    f"Generating content for lead {i+1}/{len(ranked_leads)}: {lead.get('company', 'Unknown')}"
                )
                
                message = self._generate_single_message(lead, persona, tone)
                messages.append(message)
                
            except Exception as e:
                self.log_reasoning(
                    "content_generation_error",
                    f"Failed to generate content for lead {i+1}: {str(e)}"
                )
                # Add fallback message
                messages.append(self._create_fallback_message(lead))
        
        self.log_reasoning(
            "content_generation_complete",
            f"Content generation completed: {len(messages)} messages generated"
        )
        
        return {
            "messages": messages,
            "content_metadata": {
                "total_messages": len(messages),
                "persona_used": persona,
                "tone_used": tone,
                "generation_timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_single_message(self, lead: Dict[str, Any], persona: str, tone: str) -> Dict[str, Any]:
        """
        Generate personalized message for a single lead.
        
        Args:
            lead: Lead data
            persona: Outreach persona
            tone: Message tone
            
        Returns:
            Dictionary with generated message content
        """
        if not self.openai_client:
            return self._create_fallback_message(lead)
        
        try:
            # Prepare context for the AI
            context = self._prepare_lead_context(lead)
            
            # Generate subject line
            subject = self._generate_subject_line(lead, persona, tone, context)
            
            # Generate email body
            email_body = self._generate_email_body(lead, persona, tone, context)
            
            return {
                "lead": {
                    "company": lead.get("company", ""),
                    "contact_name": lead.get("contact_name", ""),
                    "email": lead.get("email", ""),
                    "role": lead.get("role", ""),
                    "rank": lead.get("rank", 0),
                    "score": lead.get("total_score", 0)
                },
                "subject": subject,
                "email_body": email_body,
                "persona": persona,
                "tone": tone,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_reasoning(
                "message_generation_error",
                f"Error generating message for {lead.get('company', 'Unknown')}: {str(e)}"
            )
            return self._create_fallback_message(lead)
    
    def _prepare_lead_context(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context information about the lead for content generation.
        
        Args:
            lead: Lead data
            
        Returns:
            Context dictionary for AI generation
        """
        return {
            "company_name": lead.get("company", ""),
            "contact_name": lead.get("contact_name", ""),
            "contact_role": lead.get("role", ""),
            "company_industry": lead.get("company_industry", ""),
            "company_description": lead.get("company_description", ""),
            "company_size": lead.get("company_size", 0),
            "company_technologies": lead.get("company_technologies", []),
            "company_location": lead.get("company_location", ""),
            "recent_signals": lead.get("signal", ""),
            "score_breakdown": lead.get("score_breakdown", {}),
            "linkedin_profile": lead.get("linkedin", "")
        }
    
    def _generate_subject_line(self, lead: Dict[str, Any], persona: str, tone: str, context: Dict[str, Any]) -> str:
        """
        Generate personalized subject line using OpenAI.
        
        Args:
            lead: Lead data
            persona: Outreach persona
            tone: Message tone
            context: Lead context
            
        Returns:
            Generated subject line
        """
        prompt = f"""
        Generate a personalized email subject line for B2B outreach.
        
        Persona: {persona}
        Tone: {tone}
        
        Lead Context:
        - Company: {context['company_name']}
        - Contact: {context['contact_name']} ({context['contact_role']})
        - Industry: {context['company_industry']}
        - Company Size: {context['company_size']} employees
        - Recent Signal: {context['recent_signals']}
        
        Generate a compelling, personalized subject line that:
        1. Is under 50 characters
        2. Creates curiosity or urgency
        3. Is relevant to their business
        4. Avoids spam trigger words
        
        Return only the subject line, no quotes or additional text.
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=50)
            return response.strip().strip('"').strip("'")
        except Exception as e:
            self.log_reasoning("subject_generation_error", f"Error generating subject: {str(e)}")
            return f"Quick question about {context['company_name']}"
    
    def _generate_email_body(self, lead: Dict[str, Any], persona: str, tone: str, context: Dict[str, Any]) -> str:
        """
        Generate personalized email body using OpenAI.
        
        Args:
            lead: Lead data
            persona: Outreach persona
            tone: Message tone
            context: Lead context
            
        Returns:
            Generated email body
        """
        prompt = f"""
        Generate a personalized B2B outreach email for a {persona} persona.
        
        Tone: {tone}
        
        Lead Context:
        - Company: {context['company_name']}
        - Contact: {context['contact_name']} ({context['contact_role']})
        - Industry: {context['company_industry']}
        - Company Description: {context['company_description']}
        - Company Size: {context['company_size']} employees
        - Technologies: {', '.join(context['company_technologies'][:5])}
        - Location: {context['company_location']}
        - Recent Signal: {context['recent_signals']}
        
        Generate a professional, personalized email that:
        1. Is 100-200 words
        2. References specific details about their company
        3. Provides clear value proposition
        4. Includes a specific call-to-action
        5. Is personalized and not generic
        6. Maintains the {tone} tone
        
        Structure:
        - Opening: Personalized greeting and relevant observation
        - Value proposition: What you can offer them
        - Social proof: Brief credibility indicator
        - Call-to-action: Specific next step
        - Professional closing
        
        Return only the email body, no subject line or signatures.
        """
        
        try:
            response = self._call_openai(prompt, max_tokens=300)
            return response.strip()
        except Exception as e:
            self.log_reasoning("body_generation_error", f"Error generating email body: {str(e)}")
            return self._create_fallback_email_body(context)
    
    def _call_openai(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Call OpenAI API for content generation.
        
        Args:
            prompt: Prompt for the AI
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated content
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        response = self.openai_client["session"].post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_client['config']['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.openai_client["config"].get("model", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": "You are an expert B2B sales copywriter who creates highly personalized, engaging outreach emails."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def _create_fallback_message(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback message when AI generation fails.
        
        Args:
            lead: Lead data
            
        Returns:
            Fallback message dictionary
        """
        company = lead.get("company", "your company")
        contact_name = lead.get("contact_name", "")
        
        greeting = f"Hi {contact_name}," if contact_name else "Hi there,"
        
        return {
            "lead": {
                "company": company,
                "contact_name": contact_name,
                "email": lead.get("email", ""),
                "role": lead.get("role", ""),
                "rank": lead.get("rank", 0),
                "score": lead.get("total_score", 0)
            },
            "subject": f"Quick question about {company}",
            "email_body": f"""{greeting}

I hope this email finds you well. I came across {company} and was impressed by your work in the industry.

I wanted to reach out because I believe we might have some solutions that could be valuable for your team. I'd love to learn more about your current challenges and see if there's a way we can help.

Would you be open to a brief 15-minute conversation this week to explore potential synergies?

Best regards,
[Your Name]""",
            "persona": "SDR",
            "tone": "friendly",
            "generated_at": datetime.now().isoformat(),
            "fallback": True
        }
    
    def _create_fallback_email_body(self, context: Dict[str, Any]) -> str:
        """Create a simple fallback email body."""
        company = context.get("company_name", "your company")
        contact_name = context.get("contact_name", "")
        
        greeting = f"Hi {contact_name}," if contact_name else "Hi there,"
        
        return f"""{greeting}

I hope this email finds you well. I came across {company} and was impressed by your work in the industry.

I wanted to reach out because I believe we might have some solutions that could be valuable for your team. I'd love to learn more about your current challenges and see if there's a way we can help.

Would you be open to a brief 15-minute conversation this week to explore potential synergies?

Best regards,
[Your Name]"""
