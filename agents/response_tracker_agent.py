"""
ResponseTrackerAgent - Tracks email responses and engagement.

This agent monitors email responses, opens, clicks, and meeting bookings
using Apollo API and other tracking services.
"""

import requests
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentInput


class ResponseTrackerAgent(BaseAgent):
    """
    Agent responsible for tracking email responses and engagement.
    
    Monitors campaign performance using Apollo API and other tracking
    services to measure open rates, click rates, and responses.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the ResponseTrackerAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.apollo_client = None
        self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> None:
        """Initialize API clients for response tracking."""
        for tool_name, tool_instance in self._initialized_tools.items():
            if tool_name == "ApolloAPI":
                self.apollo_client = tool_instance
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """Create API client tools."""
        if tool_name == "ApolloAPI":
            return {
                "name": tool_name,
                "config": config,
                "session": requests.Session()
            }
        return super()._create_tool(tool_name, config)
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute response tracking for the campaign.
        
        Args:
            input_data: Contains campaign ID to track
            
        Returns:
            Dictionary containing response data
        """
        campaign_id = input_data.data.get("campaign_id", "")
        
        self.log_reasoning(
            "tracking_start",
            f"Starting response tracking for campaign: {campaign_id}"
        )
        
        if not campaign_id:
            self.log_reasoning("tracking_error", "No campaign ID provided")
            return {
                "responses": [],
                "tracking_metadata": {
                    "error": "No campaign ID provided",
                    "tracking_timestamp": datetime.now().isoformat()
                }
            }
        
        # Track responses using available services
        responses = []
        
        if self.apollo_client:
            apollo_responses = self._track_apollo_responses(campaign_id)
            responses.extend(apollo_responses)
        
        # Calculate engagement metrics
        metrics = self._calculate_engagement_metrics(responses)
        
        self.log_reasoning(
            "tracking_complete",
            f"Response tracking completed: {len(responses)} responses found",
            metrics
        )
        
        return {
            "responses": responses,
            "engagement_metrics": metrics,
            "tracking_metadata": {
                "campaign_id": campaign_id,
                "total_responses": len(responses),
                "tracking_timestamp": datetime.now().isoformat()
            }
        }
    
    def _track_apollo_responses(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Track responses using Apollo API.
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            List of response data
        """
        if not self.apollo_client:
            return []
        
        try:
            # Get sequence activities from Apollo
            response = self.apollo_client["session"].get(
                "https://api.apollo.io/v1/mixed_sequences/activities",
                headers={
                    "Cache-Control": "no-cache",
                    "Content-Type": "application/json",
                    "X-Api-Key": self.apollo_client["config"]["api_key"]
                },
                params={
                    "sequence_id": campaign_id,
                    "per_page": 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_apollo_responses(data)
            else:
                self.log_reasoning(
                    "apollo_tracking_error",
                    f"Apollo tracking API error: {response.status_code}"
                )
                return []
                
        except Exception as e:
            self.log_reasoning(
                "apollo_tracking_exception",
                f"Apollo tracking exception: {str(e)}"
            )
            return []
    
    def _parse_apollo_responses(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Apollo API response data into standardized format.
        
        Args:
            data: Apollo API response data
            
        Returns:
            List of parsed response data
        """
        responses = []
        
        for activity in data.get("activities", []):
            response = {
                "activity_id": activity.get("id", ""),
                "contact_email": activity.get("contact", {}).get("email", ""),
                "contact_name": activity.get("contact", {}).get("name", ""),
                "activity_type": activity.get("type", ""),
                "status": activity.get("status", ""),
                "timestamp": activity.get("created_at", ""),
                "metadata": {
                    "sequence_id": activity.get("sequence_id", ""),
                    "step_id": activity.get("step_id", ""),
                    "subject": activity.get("subject", ""),
                    "opened": activity.get("opened", False),
                    "clicked": activity.get("clicked", False),
                    "replied": activity.get("replied", False),
                    "bounced": activity.get("bounced", False)
                }
            }
            responses.append(response)
        
        return responses
    
    def _calculate_engagement_metrics(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate engagement metrics from response data.
        
        Args:
            responses: List of response data
            
        Returns:
            Dictionary with engagement metrics
        """
        if not responses:
            return {
                "total_activities": 0,
                "emails_sent": 0,
                "emails_opened": 0,
                "emails_clicked": 0,
                "emails_replied": 0,
                "emails_bounced": 0,
                "open_rate": 0.0,
                "click_rate": 0.0,
                "reply_rate": 0.0,
                "bounce_rate": 0.0
            }
        
        total_activities = len(responses)
        emails_sent = len([r for r in responses if r.get("activity_type") == "email"])
        emails_opened = len([r for r in responses if r.get("metadata", {}).get("opened", False)])
        emails_clicked = len([r for r in responses if r.get("metadata", {}).get("clicked", False)])
        emails_replied = len([r for r in responses if r.get("metadata", {}).get("replied", False)])
        emails_bounced = len([r for r in responses if r.get("metadata", {}).get("bounced", False)])
        
        # Calculate rates
        open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0.0
        click_rate = (emails_clicked / emails_sent * 100) if emails_sent > 0 else 0.0
        reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0.0
        bounce_rate = (emails_bounced / emails_sent * 100) if emails_sent > 0 else 0.0
        
        return {
            "total_activities": total_activities,
            "emails_sent": emails_sent,
            "emails_opened": emails_opened,
            "emails_clicked": emails_clicked,
            "emails_replied": emails_replied,
            "emails_bounced": emails_bounced,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "bounce_rate": round(bounce_rate, 2)
        }
    
    def _get_response_summary(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of responses for reporting.
        
        Args:
            responses: List of response data
            
        Returns:
            Summary dictionary
        """
        if not responses:
            return {"summary": "No responses found"}
        
        # Group by activity type
        by_type = {}
        for response in responses:
            activity_type = response.get("activity_type", "unknown")
            if activity_type not in by_type:
                by_type[activity_type] = []
            by_type[activity_type].append(response)
        
        # Group by status
        by_status = {}
        for response in responses:
            status = response.get("status", "unknown")
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(response)
        
        return {
            "total_responses": len(responses),
            "by_activity_type": {k: len(v) for k, v in by_type.items()},
            "by_status": {k: len(v) for k, v in by_status.items()},
            "recent_responses": sorted(
                responses,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[:10]  # Last 10 responses
        }
