"""DAX-style validation tests using source CSV calculations."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
SALES_FILE = RAW_DIR / "sales_2022_2024.csv"
BUDGET_FILE = RAW_DIR / "finance_budget.csv"


def sales() -> pd.DataFrame:
    df = pd.read_csv(SALES_FILE)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def budget() -> pd.DataFrame:
    return pd.read_csv(BUDGET_FILE)


class TestCoreMeasures:
    def test_total_sales_measure(self):
        df = sales()
        dax_total_sales = df["sales_amount"].sum()
        source_total_sales = sum(df["sales_amount"])
        assert round(dax_total_sales, 2) == round(source_total_sales, 2)

    def test_total_profit_measure(self):
        df = sales()
        assert round(df["profit_amount"].sum(), 2) == round(
            (df["sales_amount"] - df["cost_amount"]).sum(), 2
        )

    def test_profit_margin_measure(self):
        df = sales()
        expected_margin = df["profit_amount"].sum() / df["sales_amount"].sum()
        assert -1 < expected_margin < 1

    def test_average_discount_measure(self):
        df = sales()
        avg_discount = df["discount_pct"].mean()
        assert 0 <= avg_discount <= 1


class TestBudgetMeasures:
    def test_budget_actuals_reconcile_to_sales_by_month_region(self):
        df = sales()
        df["year"] = df["order_date"].dt.year
        df["month"] = df["order_date"].dt.month
        source = (
            df.groupby(["year", "month", "region"], as_index=False)["sales_amount"]
            .sum()
            .rename(columns={"sales_amount": "expected_actual"})
        )
        merged = budget().merge(source, on=["year", "month", "region"], how="left")
        difference = (merged["actual_amount"] - merged["expected_actual"]).abs().max()
        assert difference < 0.01

    def test_budget_variance_formula(self):
        bgt = budget()
        variance = bgt["actual_amount"].sum() - bgt["budget_amount"].sum()
        variance_pct = variance / bgt["budget_amount"].sum()
        assert pd.notna(variance_pct)
        assert -0.25 <= variance_pct <= 0.25


class TestVisualLevelAggregates:
    def test_region_sales_total_matches_grand_total(self):
        df = sales()
        region_total = df.groupby("region")["sales_amount"].sum().sum()
        grand_total = df["sales_amount"].sum()
        assert round(region_total, 2) == round(grand_total, 2)

    def test_category_sales_total_matches_grand_total_after_join(self):
        df = sales()
        products = pd.read_csv(RAW_DIR / "products.csv")
        joined = df.merge(products[["product_id", "category"]], on="product_id", how="left")
        category_total = joined.groupby("category")["sales_amount"].sum().sum()
        assert round(category_total, 2) == round(df["sales_amount"].sum(), 2)

    def test_monthly_trend_has_no_missing_months(self):
        df = sales()
        monthly = df.set_index("order_date").resample("MS")["sales_amount"].sum()
        assert len(monthly) == 36
        assert monthly.gt(0).all()
