"""
FeedbackTrainerAgent - Analyzes campaign performance and suggests improvements.

This agent analyzes campaign performance data and generates recommendations
for improving future campaigns, including ICP adjustments and messaging changes.
"""

import json
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentInput
from .google_sheets_client import GoogleSheetsClient


class FeedbackTrainerAgent(BaseAgent):
    """
    Agent responsible for analyzing campaign performance and generating recommendations.
    
    Uses response data to identify patterns and suggest improvements
    for future campaigns, including ICP adjustments and messaging changes.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the FeedbackTrainerAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.google_sheets_client = None
        self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> None:
        """Initialize API clients for feedback analysis."""
        for tool_name, tool_instance in self._initialized_tools.items():
            if tool_name == "GoogleSheets":
                self.google_sheets_client = tool_instance
    
    def _create_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """Create API client tools."""
        if tool_name == "GoogleSheets":
            try:
                # Extract credentials and sheet_id from config
                credentials_file = config.get("credentials")
                sheet_id = config.get("sheet_id")
                
                if not sheet_id:
                    raise ValueError("SHEET_ID is required for Google Sheets integration")
                
                # Create Google Sheets client
                sheets_client = GoogleSheetsClient(
                    sheet_id=sheet_id,
                    credentials_file=credentials_file
                )
                
                return {
                    "name": tool_name,
                    "config": config,
                    "client": sheets_client
                }
            except Exception as e:
                self.log_reasoning(
                    "google_sheets_init_error",
                    f"Failed to initialize Google Sheets client: {str(e)}"
                )
                return {
                    "name": tool_name,
                    "config": config,
                    "client": None,
                    "error": str(e)
                }
        
        return super()._create_tool(tool_name, config)
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute feedback analysis and generate recommendations.
        
        Args:
            input_data: Contains response data and engagement metrics
            
        Returns:
            Dictionary containing recommendations
        """
        responses = input_data.data.get("responses", [])
        engagement_metrics = input_data.data.get("engagement_metrics", {})
        
        self.log_reasoning(
            "feedback_analysis_start",
            f"Starting feedback analysis for {len(responses)} responses"
        )
        
        # Analyze performance patterns
        analysis = self._analyze_performance_patterns(responses, engagement_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        
        # Write recommendations to Google Sheets
        if self.google_sheets_client and self.google_sheets_client.get("client"):
            self._write_recommendations_to_sheets(recommendations)
            self._write_performance_metrics_to_sheets(analysis)
        
        self.log_reasoning(
            "feedback_analysis_complete",
            f"Feedback analysis completed: {len(recommendations)} recommendations generated",
            {"recommendation_types": [r.get("type") for r in recommendations]}
        )
        
        return {
            "recommendations": recommendations,
            "analysis": analysis,
            "feedback_metadata": {
                "total_responses_analyzed": len(responses),
                "recommendations_generated": len(recommendations),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
    
    def _analyze_performance_patterns(self, responses: List[Dict[str, Any]], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance patterns from response data.
        
        Args:
            responses: Response data
            metrics: Engagement metrics
            
        Returns:
            Analysis results
        """
        analysis = {
            "performance_summary": metrics,
            "response_patterns": {},
            "engagement_insights": {},
            "timing_analysis": {},
            "content_analysis": {}
        }
        
        # Analyze response patterns by activity type
        by_activity = {}
        for response in responses:
            activity_type = response.get("activity_type", "unknown")
            if activity_type not in by_activity:
                by_activity[activity_type] = []
            by_activity[activity_type].append(response)
        
        analysis["response_patterns"] = {
            "by_activity_type": {k: len(v) for k, v in by_activity.items()},
            "most_common_activity": max(by_activity.keys(), key=lambda k: len(by_activity[k])) if by_activity else None
        }
        
        # Analyze engagement insights
        open_rate = metrics.get("open_rate", 0)
        click_rate = metrics.get("click_rate", 0)
        reply_rate = metrics.get("reply_rate", 0)
        
        analysis["engagement_insights"] = {
            "open_rate_category": self._categorize_rate(open_rate, "open"),
            "click_rate_category": self._categorize_rate(click_rate, "click"),
            "reply_rate_category": self._categorize_rate(reply_rate, "reply"),
            "overall_performance": self._assess_overall_performance(open_rate, click_rate, reply_rate)
        }
        
        # Analyze timing patterns
        analysis["timing_analysis"] = self._analyze_timing_patterns(responses)
        
        # Analyze content performance
        analysis["content_analysis"] = self._analyze_content_performance(responses)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on performance analysis.
        
        Args:
            analysis: Performance analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # ICP recommendations
        icp_recs = self._generate_icp_recommendations(analysis)
        recommendations.extend(icp_recs)
        
        # Messaging recommendations
        messaging_recs = self._generate_messaging_recommendations(analysis)
        recommendations.extend(messaging_recs)
        
        # Timing recommendations
        timing_recs = self._generate_timing_recommendations(analysis)
        recommendations.extend(timing_recs)
        
        # Content recommendations
        content_recs = self._generate_content_recommendations(analysis)
        recommendations.extend(content_recs)
        
        return recommendations
    
    def _generate_icp_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ICP-related recommendations."""
        recommendations = []
        
        engagement_insights = analysis.get("engagement_insights", {})
        overall_performance = engagement_insights.get("overall_performance", "average")
        
        if overall_performance == "poor":
            recommendations.append({
                "type": "icp_adjustment",
                "priority": "high",
                "title": "Refine Ideal Customer Profile",
                "description": "Low engagement rates suggest the current ICP may not be well-targeted",
                "suggestions": [
                    "Narrow down company size criteria",
                    "Focus on specific industries with higher response rates",
                    "Adjust revenue range based on actual performance",
                    "Add more specific firmographic criteria"
                ],
                "expected_impact": "Increase response rates by 15-25%"
            })
        
        return recommendations
    
    def _generate_messaging_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate messaging-related recommendations."""
        recommendations = []
        
        engagement_insights = analysis.get("engagement_insights", {})
        open_rate = analysis.get("performance_summary", {}).get("open_rate", 0)
        reply_rate = analysis.get("performance_summary", {}).get("reply_rate", 0)
        
        if open_rate < 20:
            recommendations.append({
                "type": "subject_line_optimization",
                "priority": "high",
                "title": "Improve Subject Lines",
                "description": f"Low open rate ({open_rate}%) indicates subject lines need improvement",
                "suggestions": [
                    "Use more personalized subject lines",
                    "Add urgency or curiosity elements",
                    "Test different subject line formats",
                    "Avoid spam trigger words"
                ],
                "expected_impact": "Increase open rates by 20-30%"
            })
        
        if reply_rate < 5:
            recommendations.append({
                "type": "email_content_optimization",
                "priority": "high",
                "title": "Improve Email Content",
                "description": f"Low reply rate ({reply_rate}%) suggests content needs improvement",
                "suggestions": [
                    "Make emails more personalized",
                    "Add clear value propositions",
                    "Include social proof",
                    "Improve call-to-action clarity"
                ],
                "expected_impact": "Increase reply rates by 10-20%"
            })
        
        return recommendations
    
    def _generate_timing_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate timing-related recommendations."""
        recommendations = []
        
        timing_analysis = analysis.get("timing_analysis", {})
        
        if timing_analysis.get("suggests_timing_optimization", False):
            recommendations.append({
                "type": "timing_optimization",
                "priority": "medium",
                "title": "Optimize Send Times",
                "description": "Response patterns suggest timing could be improved",
                "suggestions": [
                    "Test different send times (Tuesday-Thursday, 10-11 AM)",
                    "Avoid Monday mornings and Friday afternoons",
                    "Consider time zone optimization",
                    "A/B test different send schedules"
                ],
                "expected_impact": "Increase engagement by 10-15%"
            })
        
        return recommendations
    
    def _generate_content_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content-related recommendations."""
        recommendations = []
        
        content_analysis = analysis.get("content_analysis", {})
        
        if content_analysis.get("suggests_content_diversification", False):
            recommendations.append({
                "type": "content_diversification",
                "priority": "medium",
                "title": "Diversify Content Approach",
                "description": "Content analysis suggests trying different approaches",
                "suggestions": [
                    "Test different email templates",
                    "Try video messages for high-value prospects",
                    "Experiment with different value propositions",
                    "A/B test different content lengths"
                ],
                "expected_impact": "Improve overall campaign performance"
            })
        
        return recommendations
    
    def _categorize_rate(self, rate: float, rate_type: str) -> str:
        """Categorize a rate as poor, average, or good."""
        thresholds = {
            "open": {"good": 25, "average": 15},
            "click": {"good": 5, "average": 2},
            "reply": {"good": 8, "average": 3}
        }
        
        if rate >= thresholds[rate_type]["good"]:
            return "good"
        elif rate >= thresholds[rate_type]["average"]:
            return "average"
        else:
            return "poor"
    
    def _assess_overall_performance(self, open_rate: float, click_rate: float, reply_rate: float) -> str:
        """Assess overall campaign performance."""
        if open_rate >= 25 and reply_rate >= 8:
            return "excellent"
        elif open_rate >= 15 and reply_rate >= 3:
            return "good"
        elif open_rate >= 10 and reply_rate >= 1:
            return "average"
        else:
            return "poor"
    
    def _analyze_timing_patterns(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing patterns in responses."""
        # This is a simplified analysis - in practice, you'd analyze actual timestamps
        return {
            "suggests_timing_optimization": len(responses) > 10,  # Placeholder logic
            "peak_response_times": ["Tuesday 10 AM", "Wednesday 2 PM"],
            "low_response_times": ["Monday 8 AM", "Friday 4 PM"]
        }
    
    def _analyze_content_performance(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content performance patterns."""
        # This is a simplified analysis - in practice, you'd analyze actual content
        return {
            "suggests_content_diversification": len(responses) > 5,  # Placeholder logic
            "high_performing_elements": ["personalization", "value proposition"],
            "low_performing_elements": ["generic messaging", "long emails"]
        }
    
    def _write_recommendations_to_sheets(self, recommendations: List[Dict[str, Any]]) -> None:
        """Write recommendations to Google Sheets for review."""
        if not self.google_sheets_client or not self.google_sheets_client.get("client"):
            self.log_reasoning(
                "sheets_skip",
                "Google Sheets client not available, skipping recommendations write"
            )
            return
        
        try:
            sheets_client = self.google_sheets_client["client"]
            
            # Create sheets if they don't exist
            sheets_client.create_sheets_if_not_exist()
            
            # Write recommendations
            success = sheets_client.write_recommendations(recommendations)
            
            if success:
                self.log_reasoning(
                    "sheets_write_success",
                    f"Successfully wrote {len(recommendations)} recommendations to Google Sheets"
                )
            else:
                self.log_reasoning(
                    "sheets_write_failed",
                    "Failed to write recommendations to Google Sheets"
                )
            
        except Exception as e:
            self.log_reasoning(
                "sheets_error",
                f"Failed to write recommendations to Google Sheets: {str(e)}"
            )
    
    def _write_performance_metrics_to_sheets(self, analysis: Dict[str, Any]) -> None:
        """Write performance metrics to Google Sheets."""
        if not self.google_sheets_client or not self.google_sheets_client.get("client"):
            return
        
        try:
            sheets_client = self.google_sheets_client["client"]
            
            # Prepare performance metrics
            metrics = {
                "engagement_insights": analysis.get("engagement_insights", {}),
                "response_patterns": analysis.get("response_patterns", {}),
                "timing_analysis": analysis.get("timing_analysis", {}),
                "content_analysis": analysis.get("content_analysis", {})
            }
            
            # Write metrics
            success = sheets_client.write_performance_metrics(metrics)
            
            if success:
                self.log_reasoning(
                    "metrics_write_success",
                    "Successfully wrote performance metrics to Google Sheets"
                )
            else:
                self.log_reasoning(
                    "metrics_write_failed",
                    "Failed to write performance metrics to Google Sheets"
                )
            
        except Exception as e:
            self.log_reasoning(
                "metrics_error",
                f"Failed to write performance metrics to Google Sheets: {str(e)}"
            )
