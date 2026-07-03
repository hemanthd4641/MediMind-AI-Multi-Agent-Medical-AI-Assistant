from typing import Dict, Any, Tuple, Optional
import structlog
from backend.app.models.medical_report import ParameterStatus

logger = structlog.get_logger(__name__)

# A simplified, easily extendable reference dictionary
# In a full production system, this could be loaded from the DB or a JSON file, accounting for Age/Sex.
REFERENCE_RANGES = {
    "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL", "critical_low": 7.0, "critical_high": 20.0},
    "rbc": {"min": 4.0, "max": 6.0, "unit": "million/uL"},
    "wbc": {"min": 4.0, "max": 11.0, "unit": "10^3/uL", "critical_low": 2.0, "critical_high": 30.0},
    "platelets": {"min": 150.0, "max": 450.0, "unit": "10^3/uL", "critical_low": 20.0, "critical_high": 1000.0},
    "blood sugar (fasting)": {"min": 70.0, "max": 100.0, "unit": "mg/dL", "critical_low": 50.0, "critical_high": 400.0},
    "blood sugar (random)": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "critical_low": 50.0, "critical_high": 400.0},
    "hba1c": {"min": 4.0, "max": 5.6, "unit": "%"},
    "vitamin d": {"min": 20.0, "max": 50.0, "unit": "ng/mL"},
    "vitamin b12": {"min": 200.0, "max": 900.0, "unit": "pg/mL"},
    "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL"},
    "urea": {"min": 7.0, "max": 20.0, "unit": "mg/dL"},
    "alt": {"min": 7.0, "max": 56.0, "unit": "U/L"},
    "ast": {"min": 8.0, "max": 48.0, "unit": "U/L"},
    "hdl": {"min": 40.0, "max": 60.0, "unit": "mg/dL"},
    "ldl": {"min": 0.0, "max": 100.0, "unit": "mg/dL"},
    "triglycerides": {"min": 0.0, "max": 150.0, "unit": "mg/dL"},
    "tsh": {"min": 0.4, "max": 4.0, "unit": "mIU/L"},
    "t3": {"min": 80.0, "max": 200.0, "unit": "ng/dL"},
    "t4": {"min": 4.5, "max": 11.2, "unit": "mcg/dL"}
}

def normalize_param_name(name: str) -> str:
    """Normalizes the parameter name for lookup."""
    name = name.lower().strip()
    # Handle synonyms or variations
    if name in ["hgb", "hb"]: return "hemoglobin"
    if name in ["plt", "platelet count"]: return "platelets"
    if name in ["glucose fasting", "fbs"]: return "blood sugar (fasting)"
    if name in ["rbs"]: return "blood sugar (random)"
    if name in ["sgpt"]: return "alt"
    if name in ["sgot"]: return "ast"
    return name

def evaluate_parameter(name: str, value: str) -> Tuple[ParameterStatus, Optional[float], Optional[float]]:
    """
    Evaluates a laboratory parameter against standard reference ranges.
    Returns: (Status, Reference Min, Reference Max)
    """
    norm_name = normalize_param_name(name)
    ref = REFERENCE_RANGES.get(norm_name)
    
    if not ref:
        return ParameterStatus.NORMAL, None, None
        
    try:
        # Extract numeric value
        num_val = float(''.join(c for c in str(value) if c.isdigit() or c == '.'))
    except ValueError:
        return ParameterStatus.NORMAL, ref.get("min"), ref.get("max")
        
    status = ParameterStatus.NORMAL
    
    # Check Critical
    if "critical_low" in ref and num_val < ref["critical_low"]:
        status = ParameterStatus.CRITICAL
    elif "critical_high" in ref and num_val > ref["critical_high"]:
        status = ParameterStatus.CRITICAL
    # Check Low/High
    elif num_val < ref["min"]:
        status = ParameterStatus.LOW
    elif num_val > ref["max"]:
        status = ParameterStatus.HIGH
        
    return status, ref["min"], ref["max"]

class ReferenceRangeEngine:
    """Service to evaluate extracted reports against standard ranges."""
    
    def process_items(self, items: list[dict]) -> list[dict]:
        processed = []
        for item in items:
            name = item.get("parameter_name", "")
            val = item.get("observed_value", "")
            
            status, r_min, r_max = evaluate_parameter(name, val)
            
            item["status"] = status
            item["reference_min"] = r_min
            item["reference_max"] = r_max
            
            processed.append(item)
            
        return processed

reference_range_engine = ReferenceRangeEngine()
