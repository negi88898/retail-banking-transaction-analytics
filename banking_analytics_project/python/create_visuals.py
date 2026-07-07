"""
Visualisations for stakeholder-facing summary (README, exec summary).
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

df_tx = pd.read_csv("../data/transactions_clean.csv")
df_cust = pd.read_csv("../data/customers_enriched.csv")
df_cat = pd.read_csv("../data/categories_clean.csv")
df_log = pd.read_csv("../data/data_quality_log.csv")

df_tx = df_tx.merge(df_cat, on="category_id", how="left")

# ---------------------------------------------------------------
# 1. Spend by category
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
spend_by_cat = df_tx.groupby("category_name")["amount_gbp"].sum().sort_values(ascending=True)
spend_by_cat.plot(kind="barh", ax=ax, color="#1f4e79")
ax.set_title("Total Customer Spend by Category (GBP)")
ax.set_xlabel("Total Spend (£)")
plt.tight_layout()
plt.savefig("../images/spend_by_category.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 2. Channel usage by customer segment
# ---------------------------------------------------------------
df_merged = df_tx.merge(df_cust[["customer_id", "segment"]], on="customer_id", how="left")
channel_seg = pd.crosstab(df_merged["segment"], df_merged["channel"], normalize="index") * 100

fig, ax = plt.subplots(figsize=(11, 6))
channel_seg.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
ax.set_title("Channel Usage by Customer Segment (%)")
ax.set_ylabel("% of Transactions")
ax.legend(title="Channel", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("../images/channel_by_segment.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 3. Data quality funnel
# ---------------------------------------------------------------
log_clean = df_log[df_log["check"] != "TOTAL"].copy()
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(log_clean["check"], log_clean["rows_affected"], color="#c0392b")
ax.set_title("Data Quality Issues Identified and Resolved per Pipeline Run")
ax.set_xlabel("Rows Affected")
plt.tight_layout()
plt.savefig("../images/data_quality_summary.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 4. Monthly spend trend
# ---------------------------------------------------------------
df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
df_tx["year_month"] = df_tx["transaction_date"].dt.to_period("M").astype(str)
monthly = df_tx.groupby("year_month")["amount_gbp"].sum()

fig, ax = plt.subplots(figsize=(11, 5))
monthly.plot(kind="line", marker="o", ax=ax, color="#1f4e79")
ax.set_title("Monthly Customer Spend Trend (GBP)")
ax.set_ylabel("Total Spend (£)")
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig("../images/monthly_trend.png", bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 5. Customer segment distribution
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
df_cust["spend_segment"].value_counts().plot(kind="bar", ax=ax, color=["#1f4e79", "#2980b9", "#5dade2", "#aed6f1"])
ax.set_title("Customer Distribution by Spend Segment")
ax.set_ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("../images/customer_segments.png", bbox_inches="tight")
plt.close()

print("All 5 charts saved to ../images/")
