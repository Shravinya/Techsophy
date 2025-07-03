from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path
import pandas as pd
import numpy as np

class VitalSigns(BaseModel):
    blood_pressure_systolic: float = Field(..., ge=60, le=200)
    blood_pressure_diastolic: float = Field(..., ge=40, le=130)
    heart_rate: float = Field(..., ge=40, le=200)
    temperature: float = Field(..., ge=35, le=42)
    respiratory_rate: float = Field(..., ge=8, le=40)

    @validator('blood_pressure_diastolic')
    def validate_blood_pressure(cls, v, values):
        if 'blood_pressure_systolic' in values and v >= values['blood_pressure_systolic']:
            raise ValueError('Diastolic pressure must be less than systolic pressure')
        return v

class Demographics(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., regex='^[MF]$')
    race: str = Field(..., min_length=1)

class LabResults(BaseModel):
    glucose: float = Field(..., ge=0, le=500)
    cholesterol: float = Field(..., ge=0, le=600)

class EHRRecord(BaseModel):
    patient_id: str = Field(..., regex='^P\d{6}$')
    timestamp: datetime
    vital_signs: VitalSigns
    medications: List[str] = Field(default_factory=list)
    diagnosis_codes: List[str] = Field(default_factory=list)
    lab_results: LabResults
    demographics: Demographics

    @validator('diagnosis_codes')
    def validate_diagnosis_codes(cls, v):
        for code in v:
            if not code.match(r'^[A-Z]\d{2}(\.\d+)?$'):
                raise ValueError(f'Invalid ICD-10 code format: {code}')
        return v

class QualityMetrics(BaseModel):
    completeness_score: float = Field(..., ge=0, le=100)
    consistency_score: float = Field(..., ge=0, le=100)
    accuracy_score: float = Field(..., ge=0, le=100)
    record_count: int = Field(..., ge=0)
    invalid_records: int = Field(..., ge=0)
    outlier_count: int = Field(..., ge=0)

class EHRPathTester:
    def __init__(self):
        self.current_time = datetime.strptime("2025-07-03 08:33:33", "%Y-%m-%d %H:%M:%S")
        self.current_user = "Shravinya"
        
        # Setup paths
        self.base_path = Path.cwd()
        self.data_path = self.base_path / "data"
        self.output_path = self.base_path / "output"
        
        # Create directories
        self.data_path.mkdir(exist_ok=True)
        self.output_path.mkdir(exist_ok=True)

    def load_ehr_data(self, file_path: Path) -> List[EHRRecord]:
        """Load and validate EHR data using Pydantic models"""
        try:
            print(f"Loading data from: {file_path}")
            df = pd.read_csv(file_path)
            records = []
            invalid_records = []
            
            for idx, row in df.iterrows():
                try:
                    # Create Pydantic models from row data
                    vital_signs = VitalSigns(
                        blood_pressure_systolic=float(row['systolic_bp']),
                        blood_pressure_diastolic=float(row['diastolic_bp']),
                        heart_rate=float(row['heart_rate']),
                        temperature=float(row['temperature']),
                        respiratory_rate=float(row.get('respiratory_rate', 16))
                    )
                    
                    demographics = Demographics(
                        age=int(row['age']),
                        gender=str(row['gender']),
                        race=str(row['race'])
                    )
                    
                    lab_results = LabResults(
                        glucose=float(row.get('glucose', 0)),
                        cholesterol=float(row.get('cholesterol', 0))
                    )
                    
                    record = EHRRecord(
                        patient_id=str(row['patient_id']),
                        timestamp=self.current_time,
                        vital_signs=vital_signs,
                        medications=str(row.get('medications', '')).split(',') if pd.notna(row.get('medications')) else [],
                        diagnosis_codes=str(row.get('diagnosis_codes', '')).split(',') if pd.notna(row.get('diagnosis_codes')) else [],
                        lab_results=lab_results,
                        demographics=demographics
                    )
                    records.append(record)
                    
                except Exception as e:
                    invalid_records.append({
                        'row': idx + 1,
                        'error': str(e),
                        'data': row.to_dict()
                    })
            
            if invalid_records:
                self._save_validation_errors(invalid_records)
            
            return records
            
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

    def _save_validation_errors(self, invalid_records: List[Dict]):
        """Save validation errors to a separate file"""
        error_file = self.output_path / f"validation_errors_{self.current_time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(error_file, 'w') as f:
            f.write(f"EHR Data Validation Errors\n")
            f.write(f"========================\n")
            f.write(f"Generated at: {self.current_time}\n")
            f.write(f"Generated by: {self.current_user}\n\n")
            
            for record in invalid_records:
                f.write(f"Row {record['row']}:\n")
                f.write(f"Error: {record['error']}\n")
                f.write("Data:\n")
                for key, value in record['data'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

    def run_quality_analysis(self, records: List[EHRRecord]) -> QualityMetrics:
        """Calculate quality metrics for the records"""
        total_records = len(records)
        if total_records == 0:
            return QualityMetrics(
                completeness_score=0,
                consistency_score=0,
                accuracy_score=0,
                record_count=0,
                invalid_records=0,
                outlier_count=0
            )

        # Calculate completeness
        completeness_scores = []
        for record in records:
            fields_present = sum([
                bool(record.vital_signs),
                bool(record.medications),
                bool(record.diagnosis_codes),
                bool(record.lab_results),
                bool(record.demographics)
            ])
            completeness_scores.append(fields_present / 5 * 100)

        # Calculate consistency
        consistency_scores = []
        for record in records:
            consistent = True
            # Check blood pressure consistency
            if record.vital_signs.blood_pressure_diastolic >= record.vital_signs.blood_pressure_systolic:
                consistent = False
            # Check if medications present when diagnosis codes exist
            if record.diagnosis_codes and not record.medications:
                consistent = False
            consistency_scores.append(100 if consistent else 0)

        # Detect outliers
        vital_signs_array = np.array([
            [r.vital_signs.blood_pressure_systolic,
             r.vital_signs.blood_pressure_diastolic,
             r.vital_signs.heart_rate,
             r.vital_signs.temperature,
             r.vital_signs.respiratory_rate] for r in records
        ])
        
        outliers = np.abs(vital_signs_array - np.mean(vital_signs_array, axis=0)) > 2 * np.std(vital_signs_array, axis=0)
        outlier_count = np.sum(np.any(outliers, axis=1))

        return QualityMetrics(
            completeness_score=np.mean(completeness_scores),
            consistency_score=np.mean(consistency_scores),
            accuracy_score=100 - (outlier_count / total_records * 100),
            record_count=total_records,
            invalid_records=0,  # Updated when loading data
            outlier_count=int(outlier_count)
        )

    def generate_report(self, file_path: Path, records: List[EHRRecord], metrics: QualityMetrics):
        """Generate detailed quality report"""
        report_file = self.output_path / f"quality_report_{self.current_time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"EHR Quality Analysis Report\n")
            f.write(f"=========================\n")
            f.write(f"Generated at: {self.current_time}\n")
            f.write(f"Generated by: {self.current_user}\n")
            f.write(f"Input file: {file_path.name}\n\n")
            
            f.write("Quality Metrics:\n")
            f.write("--------------\n")
            f.write(f"Completeness Score: {metrics.completeness_score:.2f}%\n")
            f.write(f"Consistency Score: {metrics.consistency_score:.2f}%\n")
            f.write(f"Accuracy Score: {metrics.accuracy_score:.2f}%\n\n")
            
            f.write("Record Statistics:\n")
            f.write("-----------------\n")
            f.write(f"Total Records: {metrics.record_count}\n")
            f.write(f"Invalid Records: {metrics.invalid_records}\n")
            f.write(f"Outliers Detected: {metrics.outlier_count}\n")

        return report_file

def main():
    tester = EHRPathTester()
    
    # Test files
    test_files = ['ehr_test_data_100.csv', 'ehr_test_data_1000.csv']
    
    for file_name in test_files:
        print(f"\nProcessing file: {file_name}")
        file_path = tester.data_path / file_name
        
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            continue
            
        # Load and validate data
        records = tester.load_ehr_data(file_path)
        if not records:
            print("No valid records found")
            continue
            
        # Calculate quality metrics
        metrics = tester.run_quality_analysis(records)
        
        # Generate report
        report_file = tester.generate_report(file_path, records, metrics)
        
        print(f"\nResults for {file_name}:")
        print(f"- Records processed: {metrics.record_count}")
        print(f"- Completeness: {metrics.completeness_score:.2f}%")
        print(f"- Consistency: {metrics.consistency_score:.2f}%")
        print(f"- Accuracy: {metrics.accuracy_score:.2f}%")
        print(f"- Report saved to: {report_file}")

if __name__ == '__main__':
    main()
