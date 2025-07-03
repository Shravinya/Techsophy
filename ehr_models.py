from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class EHRRecord:
    patient_id: str
    timestamp: datetime
    vital_signs: Dict[str, float]
    medications: List[str]
    diagnosis_codes: List[str]
    lab_results: Dict[str, float]
    demographics: Dict[str, Any]
    notes: Optional[str] = None

@dataclass
class ValidationResult:
    field_name: str
    is_valid: bool
    error_message: Optional[str] = None
    severity: str = "low"  # low, medium, high

@dataclass
class QualityReport:
    completeness_score: float
    consistency_score: float
    accuracy_score: float
    validation_results: List[ValidationResult]
    timestamp: datetime
    record_count: int