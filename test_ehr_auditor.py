import pandas as pd
from datetime import datetime
import csv
from ehr_models import EHRRecord
from ehr_quality_auditor import EHRQualityAuditor

def load_ehr_data(file_path: str) -> list:
    """
    Load EHR data from CSV file and convert to EHRRecord objects
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        records = []
        
        for _, row in df.iterrows():
            try:
                # Convert row data to EHRRecord format
                # Adjust these field mappings according to your CSV structure
                record = EHRRecord(
                    patient_id=str(row.get('patient_id', '')),
                    timestamp=datetime.now(),  # Use actual timestamp from CSV if available
                    vital_signs={
                        "blood_pressure_systolic": float(row.get('systolic_bp', 0)),
                        "blood_pressure_diastolic": float(row.get('diastolic_bp', 0)),
                        "heart_rate": float(row.get('heart_rate', 0)),
                        "temperature": float(row.get('temperature', 0)),
                        "respiratory_rate": float(row.get('respiratory_rate', 0))
                    },
                    medications=str(row.get('medications', '')).split(',') if pd.notna(row.get('medications')) else [],
                    diagnosis_codes=str(row.get('diagnosis_codes', '')).split(',') if pd.notna(row.get('diagnosis_codes')) else [],
                    lab_results={
                        "glucose": float(row.get('glucose', 0)),
                        "cholesterol": float(row.get('cholesterol', 0))
                    },
                    demographics={
                        "age": int(row.get('age', 0)),
                        "gender": str(row.get('gender', '')),
                        "race": str(row.get('race', ''))
                    },
                    notes=str(row.get('notes', '')) if pd.notna(row.get('notes')) else None
                )
                records.append(record)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
                
        return records
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return []

def run_test():
    print("EHR Data Quality Audit Test")
    print("==========================")
    print(f"Test Date/Time: 2025-07-03 08:19:31")
    print(f"User: Shravinya")
    print("\nLoading data...")
    
    # Load data from your CSV file
    file_path = r"C:\Users\SHRAVINYA\Downloads\EHR.csv"
    records = load_ehr_data(file_path)
    
    if not records:
        print("No records loaded. Please check the CSV file format.")
        return
    
    print(f"\nSuccessfully loaded {len(records)} records.")
    
    # Initialize the auditor
    auditor = EHRQualityAuditor()
    
    # Process records and get quality report
    print("\nAnalyzing data quality...")
    quality_report = auditor.process_records(records)
    
    # Print detailed report
    print("\nQuality Analysis Results:")
    print(auditor.generate_report_summary(quality_report))
    
    # Print additional statistics
    print("\nDetailed Statistics:")
    print(f"Total Records Processed: {len(records)}")
    print(f"Records with Issues: {len([r for r in quality_report.validation_results if not r.is_valid])}")
    
    # Save report to file
    report_file = "ehr_quality_report.txt"
    with open(report_file, 'w') as f:
        f.write(auditor.generate_report_summary(quality_report))
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    run_test()