# BUG-002: Region Slicer Does Not Filter Budget Table

## Summary

The region slicer filters sales visuals correctly but does not filter the Finance vs Budget table.

## Severity

P2 High

## Environment

- Report: Sales and Finance Performance Dashboard
- Page: Finance Analysis
- Visual: Finance vs Budget table
- Filter: Region slicer

## Steps To Reproduce

1. Open the Finance Analysis page.
2. Select `North` from the region slicer.
3. Compare the Sales KPI and Finance vs Budget table.
4. Repeat the same test for South, East, and West.

## Expected Result

All visuals on the page should respect the selected region filter.

## Actual Result

Sales visuals update based on the selected region, but the Finance vs Budget table continues to show all-region values.

## Root Cause

The slicer interaction or model relationship is not configured correctly for the finance budget visual. The issue is likely caused by an unsynced slicer or missing relationship between the region field used by Sales and FinanceBudget.

## Suggested Fix

1. Create a shared Region dimension table.
2. Relate both Sales and FinanceBudget to the Region dimension.
3. Use the Region dimension field in slicers.
4. Validate visual interactions on every report page.

## Regression Test

Add a validation that budget totals change when grouped by selected region:

```bash
pytest tests/test_dax_validation.py::TestBudgetMeasures -v
```

## Status

Open for demonstration. This bug is useful for interview discussion because it shows Power BI filter context knowledge.
