import structlog
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.health_timeline import HealthEvent, HealthInsight

from backend.app.ai.agents.timeline_agent import TimelineAgent
from backend.app.ai.agents.trend_analysis_agent import TrendAnalysisAgent
from backend.app.ai.agents.risk_insight_agent import RiskInsightAgent
from backend.app.ai.agents.comparison_agent import ComparisonAgent
from backend.app.ai.agents.personalized_recommendation_agent import PersonalizedRecommendationAgent

logger = structlog.get_logger(__name__)

class HealthIntelligenceCrew:
    """Orchestrates the Personalized Health Intelligence generation."""

    def __init__(self):
        self.timeline_agent = TimelineAgent()
        self.trend_agent = TrendAnalysisAgent()
        self.risk_agent = RiskInsightAgent()
        self.comparison_agent = ComparisonAgent()
        self.rec_agent = PersonalizedRecommendationAgent()

    async def run(self, db: Session, patient_profile: Any, history: List[str], raw_trends: Dict[str, Any], comparison_data: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("HealthIntelligenceCrew started")
        
        # 1. Timeline Narrative
        timeline_res = await self.timeline_agent.run(events)
        
        # 2. Trend Analysis
        trend_res = await self.trend_agent.run(raw_trends)
        
        # 3. Risk Insights
        risk_res = await self.risk_agent.run(patient_profile, raw_trends, history)
        
        # 4. Comparison
        comp_res = await self.comparison_agent.run(comparison_data)
        
        # Aggregate insights for recommendations
        all_insights = []
        all_insights.extend(trend_res.get("trend_insights", []))
        all_insights.extend(risk_res.get("risk_insights", []))
        all_insights.extend(comp_res.get("comparison_insights", []))
        
        # 5. Recommendations
        rec_res = await self.rec_agent.run(all_insights)
        all_insights.extend(rec_res.get("recommendations", []))
        
        # Save insights to DB
        if patient_profile:
            patient_id = patient_profile.user_id
            
            # Optionally clear old insights or just append
            # For simplicity, append
            for ins in all_insights:
                db_insight = HealthInsight(
                    patient_id=patient_id,
                    title=ins.get("title") or ins.get("parameter") or "Insight",
                    description=ins.get("description") or ins.get("clinical_context") or "Detail",
                    category=ins.get("category", "TREND")
                )
                db.add(db_insight)
            db.commit()

        logger.info("HealthIntelligenceCrew completed")
        
        return {
            "narrative": timeline_res,
            "insights": all_insights
        }

health_intelligence_crew = HealthIntelligenceCrew()
