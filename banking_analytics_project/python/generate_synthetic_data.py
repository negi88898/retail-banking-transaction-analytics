"""
Generate synthetic retail banking data that mirrors a real core-banking
extract: customers, categories, and transactions.

Note: This is synthetic data generated for portfolio purposes — no real
customer data is used. Intentional data quality issues (duplicates, nulls,
invalid dates, bad amounts) are injected so the QA framework has real
issues to catch and log, matching REQ-03 in the BRD.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker("en_GB")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N_CUSTOMERS = 500
N_TRANSACTIONS = 12000

# ---------------------------------------------------------------
# 1. DIM CUSTOMER
# ---------------------------------------------------------------
regions = ["London", "South East", "North West", "Scotland", "Wales",
           "Yorkshire", "West Midlands", "East of England"]
segments = ["Mass Market", "Mass Affluent", "Premier", "Student"]

customers = []
for i in range(1, N_CUSTOMERS + 1):
    customers.append({
        "customer_id": f"CUST{i:05d}",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85),
        "region": random.choice(regions),
        "segment": random.choices(segments, weights=[0.5, 0.25, 0.1, 0.15])[0],
        "join_date": fake.date_between(start_date="-10y", end_date="-30d"),
    })

df_customers = pd.DataFrame(customers)

# ---------------------------------------------------------------
# 2. DIM CATEGORY
# ---------------------------------------------------------------
categories = [
    ("CAT01", "Groceries"), ("CAT02", "Utilities"), ("CAT03", "Dining & Takeaway"),
    ("CAT04", "Entertainment"), ("CAT05", "Travel"), ("CAT06", "Transport"),
    ("CAT07", "Subscriptions"), ("CAT08", "Shopping & Retail"),
    ("CAT09", "Healthcare"), ("CAT10", "Other")
]
df_categories = pd.DataFrame(categories, columns=["category_id", "category_name"])

# ---------------------------------------------------------------
# 3. FACT TRANSACTIONS (with realistic multi-currency + channel mix)
# ---------------------------------------------------------------
channels = ["Mobile App", "Online Banking", "Branch", "ATM", "Card Payment"]
channel_weights = [0.42, 0.20, 0.05, 0.08, 0.25]
currencies = ["GBP", "GBP", "GBP", "GBP", "EUR", "USD"]  # mostly GBP, some foreign spend

merchants_by_cat = {
    "Groceries": ["Tesco", "Sainsbury's", "ASDA", "Waitrose", "Aldi"],
    "Utilities": ["British Gas", "EDF Energy", "Thames Water", "EE", "Virgin Media"],
    "Dining & Takeaway": ["Deliveroo", "Just Eat", "Nando's", "Pret A Manger", "Costa Coffee"],
    "Entertainment": ["Netflix", "Cineworld", "Spotify", "Disney+", "PlayStation Store"],
    "Travel": ["British Airways", "Trainline", "Airbnb", "Booking.com", "easyJet"],
    "Transport": ["TfL", "Uber", "Shell", "BP", "National Rail"],
    "Subscriptions": ["Amazon Prime", "Apple", "Gym Membership", "The Times", "LinkedIn Premium"],
    "Shopping & Retail": ["Amazon", "John Lewis", "ASOS", "Argos", "IKEA"],
    "Healthcare": ["Boots", "Superdrug", "Bupa", "Local Pharmacy", "Specsavers"],
    "Other": ["Cash Withdrawal", "Bank Transfer", "Direct Debit", "Fee", "Misc"]
}

transactions = []
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 6, 30)

for i in range(1, N_TRANSACTIONS + 1):
    cust = random.choice(customers)
    cat_id, cat_name = random.choice(categories)
    merchant = random.choice(merchants_by_cat[cat_name])
    channel = random.choices(channels, weights=channel_weights)[0]
    currency = random.choices(currencies, weights=[0.85, 0.05, 0.03, 0.03, 0.02, 0.02])[0]

    tx_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # realistic amount ranges by category
    amount_ranges = {
        "Groceries": (5, 120), "Utilities": (30, 250), "Dining & Takeaway": (5, 80),
        "Entertainment": (5, 60), "Travel": (30, 800), "Transport": (2, 100),
        "Subscriptions": (5, 50), "Shopping & Retail": (10, 400),
        "Healthcare": (5, 150), "Other": (5, 500)
    }
    lo, hi = amount_ranges[cat_name]
    amount = round(np.random.uniform(lo, hi), 2)

    transactions.append({
        "transaction_id": f"TXN{i:07d}",
        "customer_id": cust["customer_id"],
        "category_id": cat_id,
        "transaction_date": tx_date.strftime("%Y-%m-%d"),
        "amount": amount,
        "currency": currency,
        "merchant": merchant,
        "channel": channel,
    })

df_transactions = pd.DataFrame(transactions)

# ---------------------------------------------------------------
# 4. INJECT REALISTIC DATA QUALITY ISSUES (for the QA framework to catch)
# ---------------------------------------------------------------
n = len(df_transactions)

# a) Duplicate transactions (~3%) - common real-world issue from retry/batch reload
dupe_idx = np.random.choice(n, size=int(n * 0.03), replace=False)
df_dupes = df_transactions.iloc[dupe_idx].copy()
df_transactions = pd.concat([df_transactions, df_dupes], ignore_index=True)

# b) Null customer_id or category_id (~1%) - broken join keys from source system
null_idx = np.random.choice(len(df_transactions), size=int(n * 0.01), replace=False)
df_transactions.loc[null_idx, "customer_id"] = None

# c) Invalid/future transaction dates (~0.5%) - system clock or entry errors
future_idx = np.random.choice(len(df_transactions), size=int(n * 0.005), replace=False)
df_transactions.loc[future_idx, "transaction_date"] = "2027-03-15"

# d) Negative amounts where not expected (~0.5%) - excludes legitimate refunds pattern
neg_idx = np.random.choice(len(df_transactions), size=int(n * 0.005), replace=False)
df_transactions.loc[neg_idx, "amount"] = -abs(df_transactions.loc[neg_idx, "amount"])

# e) Missing currency (~0.3%)
curr_null_idx = np.random.choice(len(df_transactions), size=int(n * 0.003), replace=False)
df_transactions.loc[curr_null_idx, "currency"] = None

df_transactions = df_transactions.sample(frac=1, random_state=42).reset_index(drop=True)

# ---------------------------------------------------------------
# 5. SAVE RAW OUTPUTS (as if extracted from core banking system)
# ---------------------------------------------------------------
df_customers.to_csv("../data/raw_customers.csv", index=False)
df_categories.to_csv("../data/raw_categories.csv", index=False)
df_transactions.to_csv("../data/raw_transactions.csv", index=False)

print(f"Customers: {len(df_customers)}")
print(f"Categories: {len(df_categories)}")
print(f"Transactions (with injected DQ issues): {len(df_transactions)}")
print(f"  - Duplicates injected: {len(df_dupes)}")
print(f"  - Null customer_id: {int(n * 0.01)}")
print(f"  - Future/invalid dates: {int(n * 0.005)}")
print(f"  - Negative amounts: {int(n * 0.005)}")
print(f"  - Missing currency: {int(n * 0.003)}")
print("\nSaved raw_customers.csv, raw_categories.csv, raw_transactions.csv to ../data/")
