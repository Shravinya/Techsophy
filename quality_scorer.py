from typing import List
from ehr_models import EHRRecord, ValidationResult, QualityReport
from datetime import datetime

class QualityScorer:
    def calculate_scores(self, records: List[EHRRecord], validation_results: List[ValidationResult]) -> QualityReport:
        completeness_score = self._calculate_completeness(records)
        consistency_score = self._calculate_consistency(records)
        accuracy_score = self._calculate_accuracy(validation_results)
        
        return QualityReport(
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            accuracy_score=accuracy_score,
            validation_results=validation_results,
            timestamp=datetime.now(),
            record_count=len(records)
        )
    
    def _calculate_completeness(self, records: List[EHRRecord]) -> float:
        total_score = 0
        
        for record in records:
            fields_present = 0
            total_fields = 7  # Total number of main fields in EHRRecord
            
            if record.patient_id: fields_present += 1
            if record.vital_signs: fields_present += 1
            if record.medications: fields_present += 1
            if record.diagnosis_codes: fields_present += 1
            if record.lab_results: fields_present += 1
            if record.demographics: fields_present += 1
            if record.notes: fields_present += 1
            
            total_score += fields_present / total_fields
        
        return (total_score / len(records)) * 100 if records else 0
    
    def _calculate_consistency(self, records: List[EHRRecord]) -> float:
        if not records:
            return 0
            
        consistent_records = 0
        for record in records:
            # Check for basic consistency rules
            if self._is_record_consistent(record):
                consistent_records += 1
                
        return (consistent_records / len(records)) * 100
    
    def _is_record_consistent(self, record: EHRRecord) -> bool:
        # Example consistency checks
        if record.vital_signs.get('blood_pressure_systolic', 0) <= record.vital_signs.get('blood_pressure_diastolic', 0):
            return False
            
        if len(record.medications) > 0 and len(record.diagnosis_codes) == 0:
            return False
            
        return True
    
    def _calculate_accuracy(self, validation_results: List[ValidationResult]) -> float:
        if not validation_results:
            return 100.0
            
        valid_results = sum(1 for result in validation_results if result.is_valid)
        return (valid_results / len(validation_results)) * 100