# Data Dictionary: Retail Banking Transaction Analytics Model

Satisfies REQ-05 (support self-service querying by non-technical stakeholders).

## DIM_CUSTOMER

| Column | Type | Description |
|---|---|---|
| customer_id | VARCHAR | Unique customer identifier (primary key) |
| first_name, last_name | VARCHAR | Customer name (synthetic data — PII in production) |
| date_of_birth | DATE | Used for age-band analysis if required |
| region | VARCHAR | UK region (London, Scotland, etc.) |
| segment | VARCHAR | Bank-assigned segment: Mass Market, Mass Affluent, Premier, Student |
| join_date | DATE | Date the customer opened their account |
| total_spend_gbp | NUMBER | Sum of all clean transaction spend, converted to GBP |
| spend_segment | VARCHAR | Derived: Low Engagement / Moderate / High Value / Premium, based on total_spend_gbp |

## DIM_CATEGORY

| Column | Type | Description |
|---|---|---|
| category_id | VARCHAR | Unique category identifier (primary key) |
| category_name | VARCHAR | Business-friendly category name (e.g. "Groceries", "Travel") |

## DIM_DATE

| Column | Type | Description |
|---|---|---|
| date_key | DATE | Calendar date (primary key) |
| year_num, month_num, quarter_num | NUMBER | Standard date parts for grouping |
| month_name, day_of_week | VARCHAR | Human-readable date parts |

## FACT_TRANSACTIONS

| Column | Type | Description |
|---|---|---|
| transaction_id | VARCHAR | Unique transaction identifier (primary key) |
| customer_id | VARCHAR | Foreign key to DIM_CUSTOMER |
| category_id | VARCHAR | Foreign key to DIM_CATEGORY |
| transaction_date | DATE | Foreign key to DIM_DATE |
| amount | NUMBER | Original transaction amount, in original currency |
| currency | VARCHAR | Currency code (GBP, EUR, USD) |
| amount_gbp | NUMBER | Amount standardised to GBP using FX rate at load time (REQ-02) |
| merchant | VARCHAR | Merchant/payee name |
| channel | VARCHAR | Mobile App, Online Banking, Branch, ATM, Card Payment |

**Note:** Only rows that passed all data quality checks (see `data_quality_log.csv`) appear in FACT_TRANSACTIONS. Excluded rows are retained in the RAW schema for audit purposes but are not available for standard analysis.

## Key Views (pre-built, ready for self-service use)

| View | Purpose |
|---|---|
| VW_SPEND_BY_CATEGORY_CHANNEL | Spend broken down by category and channel |
| VW_MONTHLY_TRENDS | Month-over-month spend and active customer trend |
| VW_CUSTOMER_SEGMENTS | Segment-level summary by region |
| VW_PRODUCT_TEAM_SECURE_SHARE | PII-free aggregated view for external team sharing (REQ-06) |
