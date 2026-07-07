"""
Data Quality Assurance Framework
==========================================================================
Satisfies REQ-03: identify and log data quality issues before they reach
reporting. Every exclusion/fix is logged with a reason - no silent drops.

Checks implemented:
  1. Duplicate transactions
  2. Missing/null foreign keys (customer_id)
  3. Invalid transaction dates (future-dated, unparseable)
  4. Unexpected negative amounts
  5. Missing currency / failed FX conversion
  6. Referential integrity (category_id exists in dimension)
"""

import pandas as pd
from datetime import datetime


def load_transformed_data(data_dir: str = "../data"):
    df_tx = pd.read_csv(f"{data_dir}/transactions_transformed.csv")
    df_categories = pd.read_csv(f"{data_dir}/categories_clean.csv")
    return df_tx, df_categories


def run_quality_checks(df_tx: pd.DataFrame, df_categories: pd.DataFrame):
    """Runs each check, logs findings, and returns a cleaned dataframe
    plus a structured issue log (for audit/traceability, per REQ-03)."""

    issues_log = []
    df = df_tx.copy()
    starting_rows = len(df)

    # --- Check 1: Exact duplicate transactions ---
    dupe_mask = df.duplicated(subset=["transaction_id"], keep="first")
    n_dupes = dupe_mask.sum()
    issues_log.append({
        "check": "Duplicate transaction_id",
        "rows_affected": int(n_dupes),
        "action_taken": "Kept first occurrence, dropped remainder",
        "severity": "Medium"
    })
    df = df[~dupe_mask]

    # --- Check 2: Missing customer_id (broken foreign key) ---
    null_cust_mask = df["customer_id"].isna()
    n_null_cust = null_cust_mask.sum()
    issues_log.append({
        "check": "Missing customer_id",
        "rows_affected": int(n_null_cust),
        "action_taken": "Excluded from customer-level analysis; retained in raw audit table",
        "severity": "High"
    })
    df = df[~null_cust_mask]

    # --- Check 3: Invalid / future-dated transactions ---
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    invalid_date_mask = df["transaction_date"].isna() | (df["transaction_date"] > today)
    n_invalid_dates = invalid_date_mask.sum()
    issues_log.append({
        "check": "Invalid or future-dated transaction_date",
        "rows_affected": int(n_invalid_dates),
        "action_taken": "Excluded pending source system correction",
        "severity": "High"
    })
    df = df[~invalid_date_mask]

    # --- Check 4: Unexpected negative amounts ---
    neg_mask = df["amount"] < 0
    n_neg = neg_mask.sum()
    issues_log.append({
        "check": "Negative transaction amount (non-refund context)",
        "rows_affected": int(n_neg),
        "action_taken": "Flagged and excluded - to be reviewed with source system owner "
                         "to confirm if these are legitimate refunds mis-tagged as purchases",
        "severity": "Medium"
    })
    df = df[~neg_mask]

    # --- Check 5: Missing currency / failed FX conversion ---
    fx_fail_mask = df["amount_gbp"].isna()
    n_fx_fail = fx_fail_mask.sum()
    issues_log.append({
        "check": "Missing currency code / failed FX conversion",
        "rows_affected": int(n_fx_fail),
        "action_taken": "Excluded from GBP-denominated analysis; raw record retained",
        "severity": "Medium"
    })
    df = df[~fx_fail_mask]

    # --- Check 6: Referential integrity - category_id must exist in dimension ---
    valid_categories = set(df_categories["category_id"])
    bad_cat_mask = ~df["category_id"].isin(valid_categories)
    n_bad_cat = bad_cat_mask.sum()
    issues_log.append({
        "check": "category_id not found in category dimension",
        "rows_affected": int(n_bad_cat),
        "action_taken": "Excluded pending dimension update",
        "severity": "Low"
    })
    df = df[~bad_cat_mask]

    ending_rows = len(df)
    total_excluded = starting_rows - ending_rows

    issues_log.append({
        "check": "TOTAL",
        "rows_affected": int(total_excluded),
        "action_taken": f"{ending_rows}/{starting_rows} rows passed all checks "
                         f"({100*ending_rows/starting_rows:.1f}% pass rate)",
        "severity": "Summary"
    })

    return df, pd.DataFrame(issues_log)


if __name__ == "__main__":
    print("=== Data Quality Assurance Run ===\n")

    df_tx, df_categories = load_transformed_data()
    df_clean, df_log = run_quality_checks(df_tx, df_categories)

    df_clean.to_csv("../data/transactions_clean.csv", index=False)
    df_log.to_csv("../data/data_quality_log.csv", index=False)

    print(df_log.to_string(index=False))
    print(f"\nClean dataset saved: transactions_clean.csv ({len(df_clean)} rows)")
    print("Full issue log saved: data_quality_log.csv")
    print("\nThis log should be reviewed each pipeline run and shared with "
          "the source system owner if any check exceeds an agreed threshold.")
