# BUG-001: Revenue KPI Shows Blank for West Region 2022

## Summary

The Revenue KPI visual displays a blank value when the report is filtered to West region and year 2022.

## Severity

P1 Critical

## Environment

- Report: Sales and Finance Performance Dashboard
- Page: Executive Summary
- Dataset: sales_2022_2024.csv
- Filter: Region = West, Year = 2022

## Steps To Reproduce

1. Open the Power BI report.
2. Navigate to the Executive Summary page.
3. Select `West` in the region slicer.
4. Select `2022` in the year slicer.
5. Observe the Revenue KPI visual.

## Expected Result

The Revenue KPI should display the total available revenue for West region in 2022 or show 0 with a clear fallback rule.

## Actual Result

The Revenue KPI displays blank because `sales_amount` contains null values for the selected filter context.

## Root Cause

The data quality layer allowed null values in a critical revenue field. The DAX measure did not handle blank values safely.

## Suggested Fix

Use a defensive DAX measure and reject null revenue rows before refresh.

```DAX
Total Sales = COALESCE(SUM(Sales[sales_amount]), 0)
```

## Regression Test

```bash
pytest tests/test_data_quality.py::TestNullChecks -v
pytest tests/test_dax_validation.py::TestCoreMeasures::test_total_sales_measure -v
```

## Status

Open for demonstration. The automated tests are designed to catch this defect before dashboard refresh.
