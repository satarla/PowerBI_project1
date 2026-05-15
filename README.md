# Power BI QA Automation Project

End-to-end QA project for a Sales and Finance Power BI dashboard. This repository demonstrates how a QA Engineer validates business intelligence reports across data quality, business rules, DAX measures, regression checks, defect reporting, and CI/CD automation.

## Resume Summary

Designed and implemented a Power BI QA framework for a Sales and Finance dashboard using Python, pytest, pandas, SQL-style validations, and GitHub Actions. Built automated data quality checks, DAX-to-source reconciliation tests, documented production-style defects, and created a CI pipeline that generates repeatable QA evidence.

## Business Scenario

The dashboard supports sales leadership and finance teams with:

- Revenue, discount, profit, and margin analysis
- Region-wise and category-wise sales performance
- Monthly actual vs budget comparison
- Product profitability tracking
- Data quality monitoring before Power BI refresh

## Architecture

```text
Faker data generator
        |
        v
CSV files in data/raw
        |
        v
Power BI model
        |
        +--> Sales fact table
        +--> Product dimension
        +--> Finance budget table
        |
        v
DAX measures and report visuals
        |
        v
QA automation layer
        |
        +--> data quality tests
        +--> DAX validation tests
        +--> defect reports
        +--> GitHub Actions pipeline
```

## Repository Structure

```text
.
├── .github/workflows/qa_pipeline.yml
├── bug_reports/
│   ├── BUG-001_null_revenue.md
│   └── BUG-002_filter_mismatch.md
├── docs/
│   └── QA_Test_Summary_Report.md
├── scripts/
│   └── generate_sample_data.py
├── tests/
│   ├── test_data_quality.py
│   └── test_dax_validation.py
├── requirements.txt
└── README.md
```

## How To Run

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py --rows 50000
pytest tests -v --html=reports/qa_report.html --self-contained-html
```

For a quick local run:

```bash
python scripts/generate_sample_data.py --rows 5000
pytest tests -v
```

## Test Coverage

| Area | Coverage |
| --- | --- |
| File checks | Required CSV files exist and are readable |
| Schema checks | Required columns and datatypes are validated |
| Null checks | Critical fields such as order_id, dates, product_id, and sales_amount |
| Duplicate checks | Primary key uniqueness for orders, products, and budget rows |
| Date checks | 2022-2024 range, ship date after order date, no future dates |
| Business rules | Positive revenue, valid discount, unit price greater than cost |
| Referential integrity | Sales product IDs must exist in product master |
| Completeness | All regions, years, and months are represented |
| DAX validation | Source totals are reconciled against expected measure formulas |
| Regression checks | Known bug scenarios are captured as repeatable tests |

## Key QA Deliverables

- `scripts/generate_sample_data.py`: creates realistic sales, product, and budget datasets using Faker
- `tests/test_data_quality.py`: validates raw data before Power BI refresh
- `tests/test_dax_validation.py`: validates DAX-style business calculations against source data
- `bug_reports/`: contains professional defect reports with steps, expected result, actual result, severity, and regression tests
- `.github/workflows/qa_pipeline.yml`: runs automated QA checks in CI
- `docs/QA_Test_Summary_Report.md`: summarizes test strategy, scope, risks, and interview talking points

## Power BI Measures To Build

```DAX
Total Sales = SUM(Sales[sales_amount])

Total Profit = SUM(Sales[profit_amount])

Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)

Average Discount % = AVERAGE(Sales[discount_pct])

Budget Variance = [Total Sales] - SUM(FinanceBudget[budget_amount])

Budget Variance % = DIVIDE([Budget Variance], SUM(FinanceBudget[budget_amount]), 0)
```

## Interview Pitch

This project simulates a real Power BI QA assignment. I created realistic sales, product, and budget data, then designed automated validations before the data reaches the dashboard. I tested file availability, schema, nulls, duplicates, business rules, date logic, product referential integrity, and DAX calculation accuracy. I also documented defects in a professional format and configured GitHub Actions so every code change runs the QA suite automatically.

The main value is that the project shows the complete QA lifecycle: test planning, data generation, automation, defect reporting, regression testing, and CI/CD evidence.
