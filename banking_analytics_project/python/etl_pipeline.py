"""
ETL Pipeline: Raw Banking Extracts -> Clean, Modelled Data
==========================================================================
Satisfies REQ-01 (consolidation) and feeds REQ-02 (currency standardisation).

Reusable, function-based (not a top-to-bottom script) so each step can be
unit tested and re-run independently - a habit worth having in a
production data team, not just for portfolio neatness.
"""

import pandas as pd
import numpy as np
import json
from api_integration import get_exchange_rates, convert_to_gbp


def load_raw_data(data_dir: str = "../data") -> dict:
    """Load all raw source extracts. Kept separate from transformation
    so raw data is never mutated in place (auditability requirement)."""
    return {
        "customers": pd.read_csv(f"{data_dir}/raw_customers.csv"),
        "categories": pd.read_csv(f"{data_dir}/raw_categories.csv"),
        "transactions": pd.read_csv(f"{data_dir}/raw_transactions.csv"),
    }


def standardise_currency(df: pd.DataFrame, rates: dict) -> pd.DataFrame:
    """Add an amount_gbp column using the FX rates dict. Rows with
    missing/unrecognised currency get amount_gbp = NaN, to be caught
    by the data quality framework rather than silently guessed at."""
    df = df.copy()
    df["amount_gbp"] = df.apply(
        lambda row: convert_to_gbp(row["amount"], row["currency"], rates), axis=1
    )
    return df


def add_date_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """Derive a proper date dimension from transaction_date - this is
    what DIM_DATE in the Snowflake star schema will be built from."""
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["month_name"] = df["transaction_date"].dt.month_name()
    df["quarter"] = df["transaction_date"].dt.quarter
    df["day_of_week"] = df["transaction_date"].dt.day_name()
    return df


def build_customer_segments(df_customers: pd.DataFrame, df_tx: pd.DataFrame) -> pd.DataFrame:
    """Enrich customer dimension with a simple spend-based segment,
    used by REQ-04/US-09 (customer segmentation for Product/Marketing)."""
    spend_summary = (
        df_tx[df_tx["amount_gbp"].notna() & (df_tx["amount_gbp"] > 0)]
        .groupby("customer_id")["amount_gbp"]
        .sum()
        .reset_index()
        .rename(columns={"amount_gbp": "total_spend_gbp"})
    )

    df = df_customers.merge(spend_summary, on="customer_id", how="left")
    df["total_spend_gbp"] = df["total_spend_gbp"].fillna(0)

    df["spend_segment"] = pd.cut(
        df["total_spend_gbp"],
        bins=[-1, 500, 2000, 5000, np.inf],
        labels=["Low Engagement", "Moderate", "High Value", "Premium"]
    )
    return df


def run_pipeline():
    print("=== ETL Pipeline: Retail Banking Transaction Data ===\n")

    raw = load_raw_data()
    print(f"Loaded: {len(raw['customers'])} customers, "
          f"{len(raw['categories'])} categories, "
          f"{len(raw['transactions'])} raw transaction rows")

    # 1. FX standardisation
    rates = get_exchange_rates()
    df_tx = standardise_currency(raw["transactions"], rates)

    # 2. Date dimension
    df_tx = add_date_dimension(df_tx)

    # 3. Customer segmentation (built AFTER quality checks would run in
    #    production - here we build a clean copy for segmentation purposes;
    #    the authoritative clean table comes from data_quality_checks.py)
    df_customers_enriched = build_customer_segments(raw["customers"], df_tx)

    # 4. Save intermediate outputs for the QA script and Snowflake load
    df_tx.to_csv("../data/transactions_transformed.csv", index=False)
    df_customers_enriched.to_csv("../data/customers_enriched.csv", index=False)
    raw["categories"].to_csv("../data/categories_clean.csv", index=False)

    print(f"\nSaved transactions_transformed.csv ({len(df_tx)} rows)")
    print(f"Saved customers_enriched.csv ({len(df_customers_enriched)} rows)")
    print("\nSegment distribution:")
    print(df_customers_enriched["spend_segment"].value_counts())

    print("\nNext step: run data_quality_checks.py to clean and log issues "
          "before this data is loaded into Snowflake.")


if __name__ == "__main__":
    run_pipeline()
