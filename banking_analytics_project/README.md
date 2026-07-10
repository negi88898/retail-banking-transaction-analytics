# Retail Banking Transaction Analytics Platform

**Author:** Ankit Singh Negi | https://www.linkedin.com/in/ankit-negi-68b645215/ | negi88898@gmail.com

An end-to-end data & analytics project simulating the work of a Data & Analytics Analyst in a retail banking environment: capturing business requirements, building a Snowflake data model, integrating a live API, enforcing data quality, and delivering self-service analytical outputs to business stakeholders.

This project was fully executed in a live Snowflake trial account (not just written as scripts) — see [Execution Notes & Debugging](#execution-notes--debugging-real-issues-found-and-fixed) below for the real issues encountered and how they were resolved.

## Business Problem

The Customer Insights team receives transaction data from multiple channels (branch, mobile, online, ATM) in inconsistent formats, with no standardised currency conversion, no automated quality checks, and no single trusted view of customer spend. This project builds that single trusted view — from raw extract to a query-ready Snowflake model with documented, traceable outputs.

## Project Structure

```
banking_analytics_project/
├── business_requirements/
│   ├── BRD.md                        # Business Requirements Document
│   ├── user_stories_backlog.md       # Agile epics, stories, sprints
│   ├── traceability_matrix.csv       # Requirement → source → output mapping
│   └── data_dictionary.md            # Self-service reference for stakeholders
├── python/
│   ├── generate_synthetic_data.py    # Synthetic banking data generator
│   ├── api_integration.py            # Live FX rate API (Requests library)
│   ├── etl_pipeline.py               # Pandas/NumPy transformation pipeline
│   ├── data_quality_checks.py        # QA framework + issue logging
│   └── create_visuals.py             # Stakeholder-facing charts
├── snowflake/
│   ├── 01_data_model.sql             # Star schema, warehouse, stage setup
│   ├── 02_load_and_stage.sql         # COPY INTO, reconciliation checks
│   ├── 03_analysis_queries.sql       # Business-question views & queries
│   └── 04_data_sharing_example.sql   # Secure View + role-based sharing pattern
├── data/                             # Generated data + logs (see below)
├── images/                           # Charts referenced in this README
└── EXECUTIVE_SUMMARY.md              # 1-page stakeholder summary
```

## Approach

- Captured business requirements as a formal BRD, broken into an Agile backlog across 3 sprints (see `user_stories_backlog.md`).
- Generated realistic transaction data (500 customers, ~12,000 transactions across 10 categories and 5 channels) with intentionally injected data quality issues — duplicates, broken foreign keys, invalid dates, bad amounts — to mirror what a real core-banking extract looks like.
- Integrated a live FX rate API (`requests` library, with retry/backoff and a documented fallback) to standardise multi-currency transactions to GBP.
- Built a data quality framework that identifies, logs, and excludes bad records with a documented reason for every exclusion — nothing is silently dropped.
- Modelled the clean data as a Snowflake star schema (fact/dimension tables), with a separate RAW schema preserved for audit purposes.
- Built self-service SQL views answering real business questions, plus a Secure View + role-based sharing pattern so the Product team can access aggregated insights without exposure to customer PII.
- Delivered a 1-page executive summary translating the technical work into a business recommendation.
- **Executed the entire pipeline end-to-end in a live Snowflake account**, debugging real data-loading and SQL syntax issues along the way (see below).

## Key Results

| Metric | Value |
|---|---|
| Raw transactions processed | 12,360 |
| Data quality pass rate | 94.9% (628 rows identified, logged, and excluded) |
| Highest spend category | Travel (highest total GBP spend, highest average transaction value) |
| Customers modelled | 500, segmented into 4 spend tiers |
| Referential integrity | 0 orphaned transactions (every fact row validated against `DIM_CUSTOMER`) |
| Secure sharing pattern | PII-free aggregated view, role-based least-privilege access |

## Data Quality Issues Identified Per Pipeline Run

![Data Quality Summary](images/data_quality_summary.png)

## Spend by Category

![Spend by Category](images/spend_by_category.png)

## Channel Usage by Customer Segment

![Channel by Segment](images/channel_by_segment.png)

## Monthly Spend Trend

![Monthly Trend](images/monthly_trend.png)

## How to Reproduce

```bash
pip install -r requirements.txt
cd python
python generate_synthetic_data.py     # creates raw extracts
python etl_pipeline.py                # FX standardisation + transformation
python data_quality_checks.py         # QA framework + logging
python create_visuals.py              # charts

# Then in a Snowflake account (free trial works):
# Run snowflake/01_data_model.sql through 04_data_sharing_example.sql in order
```

**Note on the FX API:** the original sandbox development environment had restricted outbound network access, so `api_integration.py` automatically falls back to cached rates when the live Frankfurter API is unreachable (visible in the console output when you run it). On your own machine, with normal internet access, it calls the live API directly — the retry/fallback logic is there because production integrations shouldn't assume the API is always up.

## Execution Notes & Debugging (Real Issues Found and Fixed)

This project wasn't just written — it was actually run, end to end, in a live Snowflake trial account, and two real issues came up during that process. Documenting them here deliberately, since diagnosing and fixing data issues is exactly what a Data & Analytics Analyst role calls for.

**1. `CREATE FILE FORMAT` syntax error**
The original script used `CREATE OR REPLACE FILE_FORMAT` (single token). Snowflake requires `FILE FORMAT` as two keywords for the `CREATE` statement itself (the underscore form `FILE_FORMAT` is only valid as a parameter name inside other statements, e.g. `COPY INTO ... FILE_FORMAT = (...)`). Fixed by correcting the statement to `CREATE OR REPLACE FILE FORMAT RAW.CSV_FORMAT`.

**2. Empty dimension table causing a business view to silently return 0 rows**
After loading all five source CSVs via Snowsight's UI upload wizard, `VW_SPEND_BY_CATEGORY_CHANNEL` returned zero rows despite the view compiling successfully. Root-caused by:
- Querying `FACT_TRANSACTIONS` directly — confirmed `category_id` values (`CAT01`–`CAT10`) were present and correctly loaded.
- Querying `DIM_CATEGORY` directly — returned 0 rows. The dimension table had never been populated, because the manual per-file UI upload process didn't include the `INSERT INTO DIM_CATEGORY` step that the original `02_load_and_stage.sql` script handled automatically via `COPY INTO`.
- Fixed by running a targeted backfill: `INSERT INTO DIM_CATEGORY (category_id, category_name) SELECT category_id, category_name FROM RAW.RAW_CATEGORIES;`
- Re-ran the affected view afterward and confirmed it returned correct, non-zero results.

**3. Multi-line string literal syntax error in `04_data_sharing_example.sql`**
A `COMMENT ON VIEW` statement split a single string literal across two lines as two separate quoted strings without concatenation, which Snowflake's SQL parser rejects. Fixed by merging into a single valid string literal.

This diagnostic process — checking source vs. target row counts, isolating the join, and tracing the issue back to a skipped load step — mirrors the "identify data inconsistencies, and resolve as needed" requirement from the target job description almost exactly.

## A Note on the Data

This project uses synthetic data, generated to realistically mirror a retail banking transaction extract (structure, volume, and the kinds of data quality issues a real core-banking feed produces). No real customer data is used anywhere in this project.

## Summary

Built an end-to-end banking transaction analytics platform: authored business requirements and Agile backlog, designed and executed a Snowflake star schema in a live account, integrated a live FX rate API in Python (Pandas/NumPy/Requests), built a data quality framework achieving a 94.9% clean-data pass rate on 12,000+ transactions, diagnosed and resolved real data-loading and SQL issues during live execution, and delivered secure, self-service analytical views for business stakeholders.
