# EHR Data Quality Auditor

> Electronic Health Record (EHR) data quality assessment system with Pydantic validation.
## Features

- **Pydantic Models** for robust data validation
- **CSV Dataset Support** for easy testing
- **Modular Helper Functions** for code reusability
- **Efficient Data Processing** with batch support
- **Comprehensive Quality Metrics** (completeness, consistency, accuracy)



## Usage Example

```python
from ehr_quality_auditor import EHRPathTester

# Initialize and run test
tester = EHRPathTester()
tester.run_test("ehr_test_data.csv")
```

## Key Components

- **Data Validation**: Automatic type checking and range validation
- **Helper Functions**: Data loading, analysis, and reporting
- **Quality Metrics**: Completeness, consistency, and accuracy scoring
- **Error Handling**: Detailed validation errors and logging

