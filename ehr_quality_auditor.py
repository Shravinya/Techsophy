from typing import List
from ehr_models import EHRRecord, QualityReport
from validators import EHRValidator
from outlier_detector import OutlierDetector
from quality_scorer import QualityScorer

class EHRQualityAuditor:
    def __init__(self):
        self.validator = EHRValidator()
        self.outlier_detector = OutlierDetector()
        self.quality_scorer = QualityScorer()
    
    def process_records(self, records: List[EHRRecord]) -> QualityReport:
        # Train outlier detector
        self.outlier_detector.train(records)
        
        # Collect all validation results
        validation_results = []
        
        # Perform basic validation
        for record in records:
            validation_results.extend(self.validator.validate_record(record))
        
        # Detect outliers
        validation_results.extend(self.outlier_detector.detect_outliers(records))
        
        # Generate quality report
        quality_report = self.quality_scorer.calculate_scores(records, validation_results)
        
        return quality_report

    def generate_report_summary(self, report: QualityReport) -> str:
        summary = f"""
EHR Data Quality Report
----------------------
Generated at: {report.timestamp}
Records Analyzed: {report.record_count}

Quality Scores:
- Completeness: {report.completeness_score:.2f}%
- Consistency: {report.consistency_score:.2f}%
- Accuracy: {report.accuracy_score:.2f}%

Validation Issues:
"""
        
        issues_by_severity = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for result in report.validation_results:
            if not result.is_valid:
                issues_by_severity[result.severity].append(result)
        
        for severity in ["high", "medium", "low"]:
            if issues_by_severity[severity]:
                summary += f"\n{severity.upper()} Severity Issues:\n"
                for issue in issues_by_severity[severity]:
                    summary += f"- {issue.field_name}: {issue.error_message}\n"
        
        return summary