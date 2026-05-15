# QA Test Summary Report

## Project

Sales and Finance Power BI Dashboard QA Automation

## Objective

Validate source data quality, business rules, DAX-style calculations, and regression scenarios before publishing a Power BI dashboard.

## Scope

- CSV source validation
- Product master validation
- Finance budget reconciliation
- DAX measure validation using Python source calculations
- Known defect documentation
- CI/CD automation with GitHub Actions

## Out Of Scope

- Power BI visual pixel comparison
- Gateway refresh configuration
- Production database connection testing

## Test Strategy

The strategy combines automated validation and manual Power BI report testing. Python tests validate the raw data and calculation logic before dashboard refresh. Manual test cases focus on slicers, visual interactions, bookmarks, drill-through, and export behavior.

## Entry Criteria

- Source files are available in `data/raw`
- Required Python packages are installed
- Sample data generation script runs successfully
- Power BI model uses the expected sales, product, and budget tables

## Exit Criteria

- All automated tests pass
- No P1 or P2 defects remain open for production release
- Key measures reconcile with source data
- Test report is uploaded as a CI artifact

## Risks

| Risk | Mitigation |
| --- | --- |
| Null revenue breaks KPI visuals | Automated null checks and defensive DAX |
| Slicers do not filter all visuals | Relationship and filter-context test cases |
| Budget values do not reconcile | Monthly region-level reconciliation tests |
| Data drift after refresh | Scheduled GitHub Actions run |

## Interview Talking Points

- I built the test data instead of relying on random static files, so the project is repeatable.
- I separated clean and dirty datasets to support positive and negative testing.
- I validated both data quality and business calculations, which is important for BI QA.
- I documented defects with severity, reproduction steps, root cause, and regression coverage.
- I configured CI/CD so test evidence is generated automatically.

## Resume Bullet Options

- Built an automated Power BI QA framework using Python, pandas, pytest, and GitHub Actions to validate sales and finance dashboard data.
- Created 50,000-row realistic test datasets with Faker and injected controlled defects for negative testing and regression coverage.
- Designed automated checks for schema, nulls, duplicates, business rules, referential integrity, date logic, and DAX-style calculations.
- Documented production-style BI defects covering blank KPI revenue and slicer filter-context mismatch.
