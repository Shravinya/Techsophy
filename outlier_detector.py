import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict
from ehr_models import EHRRecord, ValidationResult

class OutlierDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
    def train(self, records: List[EHRRecord]):
        # Extract numerical features for training
        features = self._extract_features(records)
        self.isolation_forest.fit(features)
    
    def detect_outliers(self, records: List[EHRRecord]) -> List[ValidationResult]:
        features = self._extract_features(records)
        predictions = self.isolation_forest.predict(features)
        
        results = []
        for i, is_inlier in enumerate(predictions):
            if is_inlier == -1:  # Outlier detected
                results.append(ValidationResult(
                    field_name="record_outlier",
                    is_valid=False,
                    error_message=f"Record {records[i].patient_id} identified as potential outlier",
                    severity="medium"
                ))
        return results
    
    def _extract_features(self, records: List[EHRRecord]) -> np.ndarray:
        features = []
        for record in records:
            record_features = [
                record.vital_signs.get('blood_pressure_systolic', 0),
                record.vital_signs.get('blood_pressure_diastolic', 0),
                record.vital_signs.get('heart_rate', 0),
                record.vital_signs.get('temperature', 0),
                len(record.medications),
                len(record.diagnosis_codes)
            ]
            features.append(record_features)
        return np.array(features)