"""
OutreachExecutorAgent - Sends outreach messages via email.

This agent handles the actual sending of personalized outreach messages
using SendGrid or Apollo API, with proper logging and tracking.
"""

import json
import requests
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentInput


class OutreachExecutorAgent(BaseAgent):
    """
    Agent responsible for executing outreach campaigns.
    
    Sends personalized messages via SendGrid or Apollo API and tracks
    delivery status for each message.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the OutreachExecutorAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.sendgrid_client = None
        self.apollo_client = None
        self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> None:
        """Initialize API clients for email sending."""
        for tool_name, tool_instance in self._initialized_tools.items():
            if tool_name == "SendGrid":
                self.sendgrid_client = tool_instance
            elif tool_name == "ApolloAPI":
                self.apollo_client = tool_instance
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """Create API client tools."""
        if tool_name in ["SendGrid", "ApolloAPI"]:
            return {
                "name": tool_name,
                "config": config,
                "session": requests.Session()
            }
        return super()._create_tool(tool_name, config)
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute outreach campaign by sending messages.
        
        Args:
            input_data: Contains messages to send
            
        Returns:
            Dictionary containing sending results
        """
        messages = input_data.data.get("messages", [])
        
        self.log_reasoning(
            "outreach_start",
            f"Starting outreach execution for {len(messages)} messages"
        )
        
        # Generate campaign ID
        campaign_id = str(uuid.uuid4())
        
        sent_status = []
        successful_sends = 0
        
        for i, message in enumerate(messages):
            try:
                self.log_reasoning(
                    "sending_message",
                    f"Sending message {i+1}/{len(messages)} to {message.get('lead', {}).get('email', 'Unknown')}"
                )
                
                send_result = self._send_single_message(message, campaign_id)
                sent_status.append(send_result)
                
                if send_result.get("success", False):
                    successful_sends += 1
                
            except Exception as e:
                self.log_reasoning(
                    "send_error",
                    f"Failed to send message {i+1}: {str(e)}"
                )
                sent_status.append({
                    "success": False,
                    "error": str(e),
                    "message_id": f"error_{i}",
                    "lead_email": message.get("lead", {}).get("email", "Unknown")
                })
        
        self.log_reasoning(
            "outreach_complete",
            f"Outreach execution completed: {successful_sends}/{len(messages)} successful",
            {"campaign_id": campaign_id, "successful_sends": successful_sends}
        )
        
        return {
            "sent_status": sent_status,
            "campaign_id": campaign_id,
            "outreach_metadata": {
                "total_messages": len(messages),
                "successful_sends": successful_sends,
                "failed_sends": len(messages) - successful_sends,
                "execution_timestamp": datetime.now().isoformat()
            }
        }
    
    def _send_single_message(self, message: Dict[str, Any], campaign_id: str) -> Dict[str, Any]:
        """
        Send a single message using available email services.
        
        Args:
            message: Message data to send
            campaign_id: Campaign identifier
            
        Returns:
            Dictionary with sending result
        """
        lead = message.get("lead", {})
        email = lead.get("email", "")
        subject = message.get("subject", "")
        email_body = message.get("email_body", "")
        
        if not email:
            return {
                "success": False,
                "error": "No email address provided",
                "message_id": None,
                "lead_email": email
            }
        
        # Try Apollo first, then SendGrid as fallback
        if self.apollo_client:
            try:
                return self._send_via_apollo(message, campaign_id)
            except Exception as e:
                self.log_reasoning("apollo_fallback", f"Apollo failed, trying SendGrid: {str(e)}")
        
        if self.sendgrid_client:
            try:
                return self._send_via_sendgrid(message, campaign_id)
            except Exception as e:
                self.log_reasoning("sendgrid_fallback", f"SendGrid also failed: {str(e)}")
        
        return {
            "success": False,
            "error": "No email service available",
            "message_id": None,
            "lead_email": email
        }
    
    def _send_via_sendgrid(self, message: Dict[str, Any], campaign_id: str) -> Dict[str, Any]:
        """
        Send message via SendGrid API.
        
        Args:
            message: Message data
            campaign_id: Campaign identifier
            
        Returns:
            SendGrid sending result
        """
        lead = message.get("lead", {})
        email = lead.get("email", "")
        contact_name = lead.get("contact_name", "")
        subject = message.get("subject", "")
        email_body = message.get("email_body", "")
        
        # Prepare SendGrid payload
        payload = {
            "personalizations": [
                {
                    "to": [{"email": email, "name": contact_name}],
                    "subject": subject
                }
            ],
            "from": {
                "email": "noreply@yourcompany.com",  # Should be configured
                "name": "Your Company Name"
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": email_body
                }
            ],
            "custom_args": {
                "campaign_id": campaign_id,
                "lead_company": lead.get("company", ""),
                "lead_role": lead.get("role", "")
            }
        }
        
        response = self.sendgrid_client["session"].post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {self.sendgrid_client['config']['api_key']}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 202:
            message_id = response.headers.get("X-Message-Id", str(uuid.uuid4()))
            return {
                "success": True,
                "message_id": message_id,
                "service": "sendgrid",
                "lead_email": email,
                "sent_at": datetime.now().isoformat()
            }
        else:
            raise Exception(f"SendGrid API error: {response.status_code} - {response.text}")
    
    def _send_via_apollo(self, message: Dict[str, Any], campaign_id: str) -> Dict[str, Any]:
        """
        Send message via Apollo API.
        
        Args:
            message: Message data
            campaign_id: Campaign identifier
            
        Returns:
            Apollo sending result
        """
        lead = message.get("lead", {})
        email = lead.get("email", "")
        contact_name = lead.get("contact_name", "")
        subject = message.get("subject", "")
        email_body = message.get("email_body", "")
        
        # Prepare Apollo payload for sequence creation with contacts included
        payload = {
            "name": f"Campaign {campaign_id}",
            "type": "sequence",
            "steps": [
                {
                    "type": "email",
                    "subject": subject,
                    "body": email_body,
                    "delay": 0
                }
            ],
            "contacts": [
                {
                    "email": email,
                    "first_name": contact_name.split()[0] if contact_name else "",
                    "last_name": " ".join(contact_name.split()[1:]) if len(contact_name.split()) > 1 else ""
                }
            ]
        }
        
        # Create sequence with contacts included
        response = self.apollo_client["session"].post(
            "https://api.apollo.io/v1/sequences",
            headers={
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "X-Api-Key": self.apollo_client["config"]["api_key"]
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            sequence_id = data.get("emailer_campaign", {}).get("id", str(uuid.uuid4()))
            
            return {
                "success": True,
                "message_id": sequence_id,
                "service": "apollo",
                "lead_email": email,
                "sent_at": datetime.now().isoformat(),
                "sequence_name": f"Campaign {campaign_id}",
                "contact_added": True
            }
        else:
            raise Exception(f"Apollo API error: {response.status_code} - {response.text}")
    
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate message data before sending.
        
        Args:
            message: Message to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["lead", "subject", "email_body"]
        
        for field in required_fields:
            if field not in message:
                return False
        
        lead = message.get("lead", {})
        if not lead.get("email"):
            return False
        
        return True
