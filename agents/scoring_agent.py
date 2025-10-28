"""
ScoringAgent - Scores and ranks leads based on configurable criteria.

This agent evaluates leads against the Ideal Customer Profile (ICP)
and assigns scores to help prioritize outreach efforts.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentInput


class ScoringAgent(BaseAgent):
    """
    Agent responsible for scoring and ranking leads based on ICP criteria.
    
    Uses configurable scoring criteria to evaluate leads and assign
    priority scores for outreach prioritization.
    """
    
    def __init__(self, agent_id: str, instructions: str, tools: List[Dict[str, Any]] = None, **kwargs):
        """Initialize the ScoringAgent."""
        super().__init__(agent_id, instructions, tools, **kwargs)
        self.scoring_criteria = []
    
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        Execute lead scoring based on ICP criteria.
        
        Args:
            input_data: Contains enriched leads and scoring criteria
            
        Returns:
            Dictionary containing ranked leads
        """
        enriched_leads = input_data.data.get("enriched_leads", [])
        scoring_criteria = input_data.data.get("scoring_criteria", {})
        
        self.log_reasoning(
            "scoring_start",
            f"Starting scoring for {len(enriched_leads)} leads with {len(scoring_criteria.get('criteria', []))} criteria"
        )
        
        # Extract scoring criteria
        self.scoring_criteria = scoring_criteria.get("criteria", [])
        
        if not self.scoring_criteria:
            self.log_reasoning("scoring_warning", "No scoring criteria provided, using default scoring")
            self.scoring_criteria = self._get_default_criteria()
        
        scored_leads = []
        
        for i, lead in enumerate(enriched_leads):
            try:
                self.log_reasoning(
                    "scoring_lead",
                    f"Scoring lead {i+1}/{len(enriched_leads)}: {lead.get('company', 'Unknown')}"
                )
                
                score_data = self._score_single_lead(lead)
                scored_lead = {**lead, **score_data}
                scored_leads.append(scored_lead)
                
            except Exception as e:
                self.log_reasoning(
                    "scoring_error",
                    f"Failed to score lead {i+1}: {str(e)}"
                )
                # Add lead with default score
                scored_leads.append({
                    **lead,
                    "total_score": 0.0,
                    "score_breakdown": {},
                    "scoring_error": str(e)
                })
        
        # Sort leads by total score (descending)
        ranked_leads = sorted(scored_leads, key=lambda x: x.get("total_score", 0), reverse=True)
        
        # Add ranking information
        for i, lead in enumerate(ranked_leads):
            lead["rank"] = i + 1
            lead["percentile"] = ((len(ranked_leads) - i) / len(ranked_leads)) * 100
        
        self.log_reasoning(
            "scoring_complete",
            f"Scoring completed: {len(ranked_leads)} leads ranked",
            {
                "top_score": ranked_leads[0].get("total_score", 0) if ranked_leads else 0,
                "average_score": sum(l.get("total_score", 0) for l in ranked_leads) / len(ranked_leads) if ranked_leads else 0
            }
        )
        
        return {
            "ranked_leads": ranked_leads,
            "scoring_metadata": {
                "total_leads": len(enriched_leads),
                "scoring_criteria_used": len(self.scoring_criteria),
                "scoring_timestamp": datetime.now().isoformat(),
                "score_range": {
                    "min": min(l.get("total_score", 0) for l in ranked_leads) if ranked_leads else 0,
                    "max": max(l.get("total_score", 0) for l in ranked_leads) if ranked_leads else 0
                }
            }
        }
    
    def _score_single_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single lead based on the configured criteria.
        
        Args:
            lead: Lead data to score
            
        Returns:
            Dictionary with scoring results
        """
        score_breakdown = {}
        total_score = 0.0
        
        for criterion in self.scoring_criteria:
            field = criterion.get("field", "")
            weight = criterion.get("weight", 0.0)
            
            if not field or weight <= 0:
                continue
            
            field_score = self._evaluate_criterion(lead, criterion)
            weighted_score = field_score * weight
            
            score_breakdown[field] = {
                "raw_score": field_score,
                "weight": weight,
                "weighted_score": weighted_score
            }
            
            total_score += weighted_score
        
        return {
            "total_score": round(total_score, 2),
            "score_breakdown": score_breakdown,
            "scored_at": datetime.now().isoformat()
        }
    
    def _evaluate_criterion(self, lead: Dict[str, Any], criterion: Dict[str, Any]) -> float:
        """
        Evaluate a single scoring criterion for a lead.
        
        Args:
            lead: Lead data
            criterion: Scoring criterion configuration
            
        Returns:
            Score between 0.0 and 1.0
        """
        field = criterion.get("field", "")
        field_value = self._get_field_value(lead, field)
        
        if field_value is None:
            return 0.0
        
        # Handle different criterion types
        if "min" in criterion and "max" in criterion:
            return self._score_range_criterion(field_value, criterion)
        elif "value" in criterion:
            return self._score_boolean_criterion(field_value, criterion)
        else:
            return self._score_generic_criterion(field_value, criterion)
    
    def _get_field_value(self, lead: Dict[str, Any], field: str) -> Any:
        """
        Get field value from lead data, handling nested fields.
        
        Args:
            lead: Lead data
            field: Field name (supports dot notation for nested fields)
            
        Returns:
            Field value or None if not found
        """
        if "." in field:
            # Handle nested fields like "company.size"
            parts = field.split(".")
            value = lead
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        else:
            return lead.get(field)
    
    def _score_range_criterion(self, value: Any, criterion: Dict[str, Any]) -> float:
        """
        Score a range-based criterion (e.g., company size, revenue).
        
        Args:
            value: Field value to evaluate
            criterion: Criterion configuration with min/max values
            
        Returns:
            Score between 0.0 and 1.0
        """
        try:
            numeric_value = float(value)
            min_val = criterion.get("min", 0)
            max_val = criterion.get("max", 1)
            
            if min_val == max_val:
                return 1.0 if numeric_value == min_val else 0.0
            
            # Normalize to 0-1 range
            if numeric_value < min_val:
                return 0.0
            elif numeric_value > max_val:
                return 1.0
            else:
                return (numeric_value - min_val) / (max_val - min_val)
                
        except (ValueError, TypeError):
            return 0.0
    
    def _score_boolean_criterion(self, value: Any, criterion: Dict[str, Any]) -> float:
        """
        Score a boolean criterion (e.g., has recent funding, is hiring).
        
        Args:
            value: Field value to evaluate
            criterion: Criterion configuration with expected value
            
        Returns:
            Score between 0.0 and 1.0
        """
        expected_value = criterion.get("value", True)
        
        if isinstance(value, bool):
            return 1.0 if value == expected_value else 0.0
        elif isinstance(value, str):
            return 1.0 if str(expected_value).lower() == value.lower() else 0.0
        else:
            return 1.0 if value == expected_value else 0.0
    
    def _score_generic_criterion(self, value: Any, criterion: Dict[str, Any]) -> float:
        """
        Score a generic criterion based on value presence and type.
        
        Args:
            value: Field value to evaluate
            criterion: Criterion configuration
            
        Returns:
            Score between 0.0 and 1.0
        """
        if value is None or value == "":
            return 0.0
        elif isinstance(value, bool):
            return 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            return 1.0 if value > 0 else 0.0
        elif isinstance(value, str):
            return 1.0 if len(value.strip()) > 0 else 0.0
        elif isinstance(value, list):
            return 1.0 if len(value) > 0 else 0.0
        else:
            return 1.0
    
    def _get_default_criteria(self) -> List[Dict[str, Any]]:
        """
        Get default scoring criteria if none are provided.
        
        Returns:
            List of default scoring criteria
        """
        return [
            {"field": "company_size", "weight": 0.3, "min": 100, "max": 1000},
            {"field": "company_revenue", "weight": 0.25, "min": 20000000, "max": 200000000},
            {"field": "recent_funding", "weight": 0.2, "value": True},
            {"field": "hiring_sales", "weight": 0.15, "value": True},
            {"field": "is_corporate_email", "weight": 0.1, "value": True}
        ]
