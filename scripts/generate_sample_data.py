"""Generate realistic sample CSV data for a Power BI QA project."""

from __future__ import annotations

import argparse
from pathlib import Path
from random import Random

import numpy as np
import pandas as pd
from faker import Faker

RAW_DIR = Path("data/raw")
DIRTY_DIR = Path("data/dirty")
REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Furniture", "Office Supplies", "Appliances"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
PAYMENT_MODES = ["Credit Card", "UPI", "Bank Transfer", "Cash"]


def make_products(fake: Faker, rng: Random, count: int = 200) -> pd.DataFrame:
    rows = []
    for i in range(1, count + 1):
        category = rng.choice(CATEGORIES)
        cost_price = round(rng.uniform(50, 900), 2)
        markup = rng.uniform(1.15, 1.85)
        rows.append(
            {
                "product_id": f"PROD-{i:04d}",
                "product_name": f"{fake.word().title()} {category[:-1]}",
                "category": category,
                "supplier": fake.company(),
                "cost_price": cost_price,
                "unit_price": round(cost_price * markup, 2),
                "is_active": rng.choice([True, True, True, False]),
            }
        )
    return pd.DataFrame(rows)


def make_sales(
    fake: Faker, rng: Random, products: pd.DataFrame, rows: int
) -> pd.DataFrame:
    start = pd.Timestamp("2022-01-01")
    end = pd.Timestamp("2024-12-31")
    date_range_days = (end - start).days
    records = []

    product_lookup = products.set_index("product_id").to_dict("index")
    product_ids = list(product_lookup)

    for i in range(1, rows + 1):
        product_id = rng.choice(product_ids)
        product = product_lookup[product_id]
        quantity = rng.randint(1, 12)
        discount_pct = round(rng.choice([0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20]), 2)
        order_date = start + pd.Timedelta(days=rng.randint(0, date_range_days))
        ship_date = order_date + pd.Timedelta(days=rng.randint(1, 7))
        gross_sales = product["unit_price"] * quantity
        sales_amount = round(gross_sales * (1 - discount_pct), 2)
        cost_amount = round(product["cost_price"] * quantity, 2)

        records.append(
            {
                "order_id": f"ORD-{i:07d}",
                "order_date": order_date.date().isoformat(),
                "ship_date": ship_date.date().isoformat(),
                "customer_name": fake.name(),
                "segment": rng.choice(SEGMENTS),
                "region": rng.choice(REGIONS),
                "state": fake.state(),
                "city": fake.city(),
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": product["unit_price"],
                "discount_pct": discount_pct,
                "sales_amount": sales_amount,
                "cost_amount": cost_amount,
                "profit_amount": round(sales_amount - cost_amount, 2),
                "payment_mode": rng.choice(PAYMENT_MODES),
            }
        )

    return pd.DataFrame(records)


def make_budget(sales: pd.DataFrame, rng: Random) -> pd.DataFrame:
    sales_copy = sales.copy()
    sales_copy["order_date"] = pd.to_datetime(sales_copy["order_date"])
    sales_copy["year"] = sales_copy["order_date"].dt.year
    sales_copy["month"] = sales_copy["order_date"].dt.month

    actuals = (
        sales_copy.groupby(["year", "month", "region"], as_index=False)["sales_amount"]
        .sum()
        .rename(columns={"sales_amount": "actual_amount"})
    )
    actuals["budget_amount"] = actuals["actual_amount"].apply(
        lambda value: round(value * rng.uniform(0.88, 1.15), 2)
    )
    actuals["budget_id"] = actuals.apply(
        lambda row: f"BUD-{int(row['year'])}-{int(row['month']):02d}-{row['region'].upper()}",
        axis=1,
    )
    return actuals[
        ["budget_id", "year", "month", "region", "budget_amount", "actual_amount"]
    ]


def make_dirty_sales(sales: pd.DataFrame, rng: Random) -> pd.DataFrame:
    dirty = sales.copy()

    def sample_index(size: int):
        return rng.sample(list(dirty.index), min(size, len(dirty)))

    dirty.loc[sample_index(max(1, int(len(dirty) * 0.08))), "sales_amount"] = np.nan
    dirty.loc[sample_index(max(1, int(len(dirty) * 0.05))), "order_date"] = np.nan
    dirty.loc[sample_index(200), "sales_amount"] = -100
    dirty.loc[sample_index(150), "discount_pct"] = 1.25
    dirty.loc[sample_index(30), "region"] = "Unknown"
    dirty.loc[sample_index(20), "product_id"] = "BAD-ID"

    ship_before_order = sample_index(100)
    dirty.loc[ship_before_order, "ship_date"] = (
        pd.to_datetime(dirty.loc[ship_before_order, "order_date"], errors="coerce")
        - pd.Timedelta(days=3)
    ).dt.date.astype(str)

    future_rows = sample_index(50)
    dirty.loc[future_rows, "order_date"] = "2025-01-15"

    duplicate_rows = dirty.sample(n=min(300, len(dirty)), random_state=42)
    dirty = pd.concat([dirty, duplicate_rows], ignore_index=True)

    bug_mask = dirty["region"].eq("West") & dirty["order_date"].astype(
        str
    ).str.startswith("2022")
    dirty.loc[bug_mask, "sales_amount"] = np.nan
    return dirty


def validate_outputs(
    sales: pd.DataFrame, products: pd.DataFrame, budget: pd.DataFrame
) -> None:
    checks = [
        (not sales.empty, "sales data is empty"),
        (not products.empty, "products data is empty"),
        (not budget.empty, "budget data is empty"),
        (sales["order_id"].is_unique, "order_id is not unique in clean sales"),
        (products["product_id"].is_unique, "product_id is not unique"),
        (budget["budget_id"].is_unique, "budget_id is not unique"),
        (
            set(sales["region"]).issubset(set(REGIONS)),
            "unexpected region in clean sales",
        ),
        (
            sales["sales_amount"].gt(0).all(),
            "clean sales contains non-positive revenue",
        ),
        (sales["discount_pct"].between(0, 1).all(), "clean sales has invalid discount"),
        (
            set(sales["product_id"]).issubset(set(products["product_id"])),
            "missing product reference",
        ),
    ]
    failures = [message for passed, message in checks if not passed]
    if failures:
        raise ValueError("Data generation failed validation: " + "; ".join(failures))


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    fake = Faker("en_US")
    fake.seed_instance(args.seed)
    rng = Random(args.seed)
    np.random.seed(args.seed)

    products = make_products(fake, rng)
    sales = make_sales(fake, rng, products, args.rows)
    budget = make_budget(sales, rng)
    dirty_sales = make_dirty_sales(sales, rng)

    validate_outputs(sales, products, budget)
    write_csv(products, RAW_DIR / "products.csv")
    write_csv(sales, RAW_DIR / "sales_2022_2024.csv")
    write_csv(budget, RAW_DIR / "finance_budget.csv")
    write_csv(dirty_sales, DIRTY_DIR / "sales_with_defects.csv")

    print("Generated Power BI QA sample data")
    print(f"Sales rows: {len(sales):,}")
    print(f"Product rows: {len(products):,}")
    print(f"Budget rows: {len(budget):,}")
    print(f"Dirty sales rows: {len(dirty_sales):,}")


if __name__ == "__main__":
    main()
