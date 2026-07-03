import structlog
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.medical_report import MedicalReport, MedicalReportItem
from collections import defaultdict

logger = structlog.get_logger(__name__)

class TrendEngine:
    """Analyzes historical medical report items to generate trends."""

    def analyze_trends(self, db: Session, patient_id: str) -> Dict[str, Any]:
        """Calculates trends for numerical lab parameters across multiple reports."""
        logger.info("Starting trend analysis", patient_id=patient_id)
        
        # Get all completed reports for the patient, ordered oldest to newest
        reports = db.query(MedicalReport).filter(
            MedicalReport.patient_id == patient_id, 
            MedicalReport.status == 'completed'
        ).order_by(MedicalReport.created_at.asc()).all()
        
        if not reports:
            return {"trends": {}}
            
        report_ids = [r.id for r in reports]
        
        # Get all items for these reports
        items = db.query(MedicalReportItem).filter(MedicalReportItem.report_id.in_(report_ids)).all()
        
        # Group by parameter name (normalized)
        parameter_series = defaultdict(list)
        
        for item in items:
            if not item.value:
                continue
                
            try:
                # Attempt to parse float, skipping non-numeric strings
                # Strip out common non-numeric chars for basic parsing (like <, >, commas)
                val_str = item.value.replace('<', '').replace('>', '').replace(',', '').strip()
                val_float = float(val_str)
                
                # Find the corresponding report date
                report_date = next(r.created_at for r in reports if r.id == item.report_id)
                
                param_name = item.parameter_name.strip().title()
                parameter_series[param_name].append({
                    "date": report_date.isoformat(),
                    "value": val_float,
                    "unit": item.unit,
                    "flag": item.abnormal_flag
                })
            except ValueError:
                # Not a simple number, skip trend plotting
                pass

        trends = {}
        for param, series in parameter_series.items():
            # Sort by date just in case
            series.sort(key=lambda x: x["date"])
            
            if len(series) < 2:
                # Not enough data for a trend
                continue
                
            first_val = series[0]["value"]
            last_val = series[-1]["value"]
            
            delta = last_val - first_val
            pct_change = (delta / first_val * 100) if first_val != 0 else 0
            
            trend_direction = "Stable"
            if pct_change > 5:
                trend_direction = "Increasing"
            elif pct_change < -5:
                trend_direction = "Decreasing"
                
            trends[param] = {
                "series": series,
                "overall_direction": trend_direction,
                "pct_change": round(pct_change, 2)
            }
            
        return {"trends": trends}

trend_engine = TrendEngine()
