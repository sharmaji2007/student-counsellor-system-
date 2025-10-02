import re
from typing import List, Dict, Any
from datetime import datetime

from app.core.config import settings

class SafetyService:
    def __init__(self):
        self.sos_keywords = [keyword.lower() for keyword in settings.SOS_KEYWORDS]
        self.sos_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for SOS keyword detection"""
        patterns = []
        
        # Add exact keyword matches
        for keyword in self.sos_keywords:
            patterns.append(re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE))
        
        # Add additional concerning patterns
        concerning_patterns = [
            r'\b(don\'t want to|can\'t) live\b',
            r'\bno point in living\b',
            r'\bwant to disappear\b',
            r'\bcan\'t take it anymore\b',
            r'\bthinking about death\b',
            r'\bsuicidal thoughts\b',
            r'\bself harm\b',
            r'\bcut myself\b',
            r'\bhurt myself\b'
        ]
        
        for pattern in concerning_patterns:
            patterns.append(re.compile(pattern, re.IGNORECASE))
        
        return patterns
    
    def check_sos_keywords(self, message: str) -> List[str]:
        """Check if message contains SOS keywords and return matched keywords"""
        matched_keywords = []
        message_lower = message.lower()
        
        # Check exact keyword matches
        for keyword in self.sos_keywords:
            if keyword in message_lower:
                matched_keywords.append(keyword)
        
        # Check pattern matches
        for pattern in self.sos_patterns:
            matches = pattern.findall(message)
            if matches:
                matched_keywords.extend(matches)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(matched_keywords))
    
    def assess_message_risk_level(self, message: str) -> Dict[str, Any]:
        """Assess the risk level of a message"""
        matched_keywords = self.check_sos_keywords(message)
        
        if not matched_keywords:
            return {
                "risk_level": "low",
                "score": 0.0,
                "keywords": [],
                "requires_intervention": False
            }
        
        # Calculate risk score based on keywords and context
        risk_score = 0.0
        high_risk_keywords = ["suicide", "kill myself", "end my life", "want to die"]
        medium_risk_keywords = ["harm myself", "hurt myself", "can't take it"]
        
        for keyword in matched_keywords:
            if any(high_risk in keyword.lower() for high_risk in high_risk_keywords):
                risk_score += 0.8
            elif any(medium_risk in keyword.lower() for medium_risk in medium_risk_keywords):
                risk_score += 0.5
            else:
                risk_score += 0.3
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = "critical"
            requires_intervention = True
        elif risk_score >= 0.5:
            risk_level = "high"
            requires_intervention = True
        elif risk_score >= 0.3:
            risk_level = "medium"
            requires_intervention = True
        else:
            risk_level = "low"
            requires_intervention = False
        
        return {
            "risk_level": risk_level,
            "score": min(risk_score, 1.0),
            "keywords": matched_keywords,
            "requires_intervention": requires_intervention
        }
    
    def generate_safety_report(self, messages: List[str]) -> Dict[str, Any]:
        """Generate a safety report from multiple messages"""
        total_messages = len(messages)
        flagged_messages = 0
        all_keywords = []
        risk_scores = []
        
        for message in messages:
            assessment = self.assess_message_risk_level(message)
            if assessment["requires_intervention"]:
                flagged_messages += 1
                all_keywords.extend(assessment["keywords"])
                risk_scores.append(assessment["score"])
        
        # Calculate overall risk
        if risk_scores:
            avg_risk_score = sum(risk_scores) / len(risk_scores)
            max_risk_score = max(risk_scores)
        else:
            avg_risk_score = 0.0
            max_risk_score = 0.0
        
        # Determine overall risk level
        if max_risk_score >= 0.8 or flagged_messages >= 3:
            overall_risk = "critical"
        elif max_risk_score >= 0.5 or flagged_messages >= 2:
            overall_risk = "high"
        elif max_risk_score >= 0.3 or flagged_messages >= 1:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "total_messages": total_messages,
            "flagged_messages": flagged_messages,
            "flagged_percentage": (flagged_messages / total_messages * 100) if total_messages > 0 else 0,
            "unique_keywords": list(set(all_keywords)),
            "avg_risk_score": avg_risk_score,
            "max_risk_score": max_risk_score,
            "overall_risk": overall_risk,
            "requires_immediate_attention": overall_risk in ["critical", "high"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_intervention_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Get intervention recommendations based on risk assessment"""
        recommendations = []
        
        risk_level = risk_assessment.get("risk_level", "low")
        keywords = risk_assessment.get("keywords", [])
        
        if risk_level == "critical":
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: Contact student immediately",
                "Notify school counselor and administration",
                "Consider involving emergency services if student is unreachable",
                "Contact parent/guardian immediately",
                "Arrange for immediate in-person check-in"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Contact student within 1 hour",
                "Schedule immediate counseling session",
                "Notify parent/guardian",
                "Increase monitoring and check-ins",
                "Provide crisis hotline information"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Contact student within 24 hours",
                "Schedule counseling session within 48 hours",
                "Consider notifying parent/guardian",
                "Provide mental health resources",
                "Monitor for escalation"
            ])
        else:
            recommendations.extend([
                "Continue regular monitoring",
                "Provide general mental health resources",
                "Encourage open communication"
            ])
        
        # Add keyword-specific recommendations
        if any("suicide" in keyword.lower() for keyword in keywords):
            recommendations.append("Suicide risk protocol activated - follow emergency procedures")
        
        if any("harm" in keyword.lower() for keyword in keywords):
            recommendations.append("Self-harm risk identified - assess for physical safety")
        
        return recommendations