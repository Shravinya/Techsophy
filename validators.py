from typing import List
import re
from datetime import datetime
from ehr_models import EHRRecord, ValidationResult

class EHRValidator:
    def __init__(self):
        self.vital_signs_ranges = {
            "blood_pressure_systolic": (60, 200),
            "blood_pressure_diastolic": (40, 130),
            "heart_rate": (40, 200),
            "temperature": (35, 42),
            "respiratory_rate": (8, 40)
        }
    
    def validate_record(self, record: EHRRecord) -> List[ValidationResult]:
        results = []
        
        # Validate patient ID format
        results.extend(self._validate_patient_id(record.patient_id))
        
        # Validate vital signs
        results.extend(self._validate_vital_signs(record.vital_signs))
        
        # Validate demographics
        results.extend(self._validate_demographics(record.demographics))
        
        # Validate diagnosis codes
        results.extend(self._validate_diagnosis_codes(record.diagnosis_codes))
        
        return results
    
    def _validate_patient_id(self, patient_id: str) -> List[ValidationResult]:
        if not re.match(r'^P\d{6}$', patient_id):
            return [ValidationResult(
                field_name="patient_id",
                is_valid=False,
                error_message="Patient ID must be in format P followed by 6 digits",
                severity="high"
            )]
        return []
    
    def _validate_vital_signs(self, vital_signs: dict) -> List[ValidationResult]:
        results = []
        for name, value in vital_signs.items():
            if name in self.vital_signs_ranges:
                min_val, max_val = self.vital_signs_ranges[name]
                if not min_val <= value <= max_val:
                    results.append(ValidationResult(
                        field_name=f"vital_signs.{name}",
                        is_valid=False,
                        error_message=f"{name} value {value} is outside normal range ({min_val}-{max_val})",
                        severity="medium"
                    ))
        return results
    
    def _validate_demographics(self, demographics: dict) -> List[ValidationResult]:
        required_fields = ["age", "gender", "race"]
        results = []
        
        for field in required_fields:
            if field not in demographics:
                results.append(ValidationResult(
                    field_name=f"demographics.{field}",
                    is_valid=False,
                    error_message=f"Missing required demographic field: {field}",
                    severity="medium"
                ))
        return results
    
    def _validate_diagnosis_codes(self, codes: List[str]) -> List[ValidationResult]:
        results = []
        icd10_pattern = r'^[A-Z]\d{2}(\.\d+)?$'
        
        for code in codes:
            if not re.match(icd10_pattern, code):
                results.append(ValidationResult(
                    field_name="diagnosis_codes",
                    is_valid=False,
                    error_message=f"Invalid ICD-10 code format: {code}",
                    severity="high"
                ))
        return results