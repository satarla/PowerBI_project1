"""Automated data quality checks for the Power BI source files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
SALES_FILE = RAW_DIR / "sales_2022_2024.csv"
PRODUCTS_FILE = RAW_DIR / "products.csv"
BUDGET_FILE = RAW_DIR / "finance_budget.csv"
VALID_REGIONS = {"North", "South", "East", "West"}


def load_csv(path: Path) -> pd.DataFrame:
    assert path.exists(), f"Missing required file: {path}"
    return pd.read_csv(path)


class TestFileExistence:
    def test_required_files_exist(self):
        for path in [SALES_FILE, PRODUCTS_FILE, BUDGET_FILE]:
            assert path.exists(), f"{path} does not exist"

    def test_files_are_not_empty(self):
        for path in [SALES_FILE, PRODUCTS_FILE, BUDGET_FILE]:
            assert not load_csv(path).empty


class TestSchemaValidation:
    def test_sales_schema(self):
        sales = load_csv(SALES_FILE)
        expected = {
            "order_id",
            "order_date",
            "ship_date",
            "customer_name",
            "segment",
            "region",
            "state",
            "city",
            "product_id",
            "quantity",
            "unit_price",
            "discount_pct",
            "sales_amount",
            "cost_amount",
            "profit_amount",
            "payment_mode",
        }
        assert expected.issubset(sales.columns)

    def test_product_schema(self):
        products = load_csv(PRODUCTS_FILE)
        expected = {
            "product_id",
            "product_name",
            "category",
            "supplier",
            "cost_price",
            "unit_price",
            "is_active",
        }
        assert expected.issubset(products.columns)

    def test_budget_schema(self):
        budget = load_csv(BUDGET_FILE)
        expected = {"budget_id", "year", "month", "region", "budget_amount", "actual_amount"}
        assert expected.issubset(budget.columns)


class TestNullChecks:
    def test_sales_critical_columns_have_no_nulls(self):
        sales = load_csv(SALES_FILE)
        critical_columns = ["order_id", "order_date", "ship_date", "product_id", "sales_amount"]
        assert sales[critical_columns].isna().sum().sum() == 0

    def test_product_critical_columns_have_no_nulls(self):
        products = load_csv(PRODUCTS_FILE)
        required = ["product_id", "category", "unit_price", "cost_price"]
        assert products[required].isna().sum().sum() == 0

    def test_budget_critical_columns_have_no_nulls(self):
        budget = load_csv(BUDGET_FILE)
        required = ["budget_id", "year", "month", "region", "budget_amount"]
        assert budget[required].isna().sum().sum() == 0


class TestDuplicateChecks:
    def test_order_id_is_unique(self):
        sales = load_csv(SALES_FILE)
        assert sales["order_id"].is_unique

    def test_product_id_is_unique(self):
        products = load_csv(PRODUCTS_FILE)
        assert products["product_id"].is_unique

    def test_budget_id_is_unique(self):
        budget = load_csv(BUDGET_FILE)
        assert budget["budget_id"].is_unique


class TestDateRangeValidation:
    def test_order_dates_are_in_reporting_period(self):
        sales = load_csv(SALES_FILE)
        order_dates = pd.to_datetime(sales["order_date"])
        assert order_dates.min() >= pd.Timestamp("2022-01-01")
        assert order_dates.max() <= pd.Timestamp("2024-12-31")

    def test_ship_date_is_not_before_order_date(self):
        sales = load_csv(SALES_FILE)
        order_dates = pd.to_datetime(sales["order_date"])
        ship_dates = pd.to_datetime(sales["ship_date"])
        assert (ship_dates >= order_dates).all()


class TestBusinessRules:
    def test_sales_amount_is_positive(self):
        sales = load_csv(SALES_FILE)
        assert sales["sales_amount"].gt(0).all()

    def test_discount_is_between_zero_and_one(self):
        sales = load_csv(SALES_FILE)
        assert sales["discount_pct"].between(0, 1).all()

    def test_product_unit_price_is_greater_than_cost_price(self):
        products = load_csv(PRODUCTS_FILE)
        assert (products["unit_price"] > products["cost_price"]).all()

    def test_profit_calculation_matches_source_formula(self):
        sales = load_csv(SALES_FILE)
        expected_profit = (sales["sales_amount"] - sales["cost_amount"]).round(2)
        pd.testing.assert_series_equal(
            sales["profit_amount"].round(2),
            expected_profit,
            check_names=False,
        )


class TestReferentialIntegrity:
    def test_sales_product_ids_exist_in_product_master(self):
        sales = load_csv(SALES_FILE)
        products = load_csv(PRODUCTS_FILE)
        missing = set(sales["product_id"]) - set(products["product_id"])
        assert not missing

    def test_sales_regions_are_valid(self):
        sales = load_csv(SALES_FILE)
        assert set(sales["region"]).issubset(VALID_REGIONS)

    def test_budget_regions_are_valid(self):
        budget = load_csv(BUDGET_FILE)
        assert set(budget["region"]).issubset(VALID_REGIONS)


class TestCompleteness:
    def test_all_years_are_present(self):
        sales = load_csv(SALES_FILE)
        years = set(pd.to_datetime(sales["order_date"]).dt.year)
        assert years == {2022, 2023, 2024}

    def test_all_months_are_present(self):
        sales = load_csv(SALES_FILE)
        months = set(pd.to_datetime(sales["order_date"]).dt.month)
        assert months == set(range(1, 13))

    def test_all_regions_are_present(self):
        sales = load_csv(SALES_FILE)
        assert set(sales["region"]) == VALID_REGIONS

    def test_minimum_row_count_for_dashboard_testing(self):
        sales = load_csv(SALES_FILE)
        assert len(sales) >= 5000
