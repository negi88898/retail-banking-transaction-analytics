# Business Requirements Document (BRD)
## Retail Banking Transaction Analytics Platform

| | |
|---|---|
| **Document Owner** | [Your Name], Data & Analytics Analyst |
| **Stakeholder** | Head of Customer Insights |
| **Status** | Approved for build |
| **Version** | 1.0 |

---

## 1. Business Context

The Customer Insights team currently receives transaction data from multiple channels (branch, mobile, online, ATM) in inconsistent formats, with no standardised currency conversion, no automated data quality checks, and no single view of customer spending behaviour. This limits the bank's ability to:

- Identify spending trends and customer segments for targeted product offers
- Detect data quality issues before they reach downstream reporting
- Respond quickly to ad-hoc analytical requests from Product and Risk teams

## 2. Business Objective

Build a single, trusted, query-ready data model in Snowflake that consolidates transaction data, standardises it (including multi-currency conversion via a live exchange rate feed), enforces data quality rules, and supports self-service analysis for the Customer Insights and Product teams.

## 3. Scope

**In scope:**
- Consolidation of customer, account, and transaction data into a Snowflake star schema
- Automated currency standardisation using a live FX rate API
- A repeatable data quality (QA) framework with a documented issue log
- A set of analytical outputs (spend by category, channel usage, customer segments, monthly trends)

**Out of scope (future phase):**
- Real-time streaming ingestion (this phase is batch)
- Predictive/ML models (recommended as Phase 2 once the data model is trusted)
- Direct write-back to source banking systems

## 4. Business Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| REQ-01 | Consolidate transaction, customer, and category data into a single queryable model | Must | Star schema in Snowflake with fact/dimension tables; row counts reconcile with source files |
| REQ-02 | Standardise all transaction amounts to GBP using current exchange rates | Must | All amounts convertible to GBP via a documented, repeatable FX lookup; conversion logic unit-tested |
| REQ-03 | Identify and log data quality issues (duplicates, nulls, invalid dates, negative amounts where not expected) | Must | A data quality log is produced on every pipeline run, listing issue type, row count, and resolution action |
| REQ-04 | Provide category- and channel-level spend analysis | Must | SQL views available in Snowflake; results validated against source data manually for 3 sample customers |
| REQ-05 | Support self-service querying by non-technical stakeholders | Should | Pre-built views with business-friendly column names; documented in a data dictionary |
| REQ-06 | Enable secure, read-only sharing of summary-level data with the Product team without duplicating data | Could | Demonstrated via Snowflake Secure View / data sharing pattern |
| REQ-07 | Pipeline should be re-runnable without manual intervention | Must | Script can be re-executed end-to-end and produces consistent output |

## 5. Non-Functional Requirements

- **Data quality:** No pipeline run should silently drop or duplicate records — all exclusions must be logged.
- **Traceability:** Every analytical output must be traceable back to the business requirement it satisfies (see traceability matrix).
- **Auditability:** Raw source data is retained unmodified; all transformations happen in a separate, versioned layer.

## 6. Assumptions & Constraints

- Source transaction data is provided as a daily batch extract (CSV) from the core banking system.
- Exchange rates are sourced from a public FX API (Frankfurter API) and refreshed on each pipeline run — in production this would use the bank's licensed FX data provider.
- This is a portfolio/demonstration project using synthetic data structured to mirror real retail banking transaction data; no real customer data is used.

## 7. Sign-off

| Role | Name | Status |
|---|---|---|
| Business Stakeholder | Head of Customer Insights | Approved |
| Data & Analytics Analyst | [Your Name] | Author |
