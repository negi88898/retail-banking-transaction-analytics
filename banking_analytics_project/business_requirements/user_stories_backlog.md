# Agile Backlog: Retail Banking Transaction Analytics Platform

Organised as Epics > User Stories, with acceptance criteria and story points (Fibonacci scale). Delivered across 3 sprints (2 weeks each).

---

## Epic 1: Data Consolidation & Modelling

**Goal:** Get raw, messy multi-source data into a single trusted Snowflake model.

| Story | As a... | I want... | So that... | Points | Sprint |
|---|---|---|---|---|---|
| US-01 | Data Analyst | to design a star schema for transaction data | analysts can query consistently without joining raw source files | 5 | 1 |
| US-02 | Data Analyst | to load customer, category, and transaction data into Snowflake staging tables | raw data is preserved unmodified for audit purposes | 3 | 1 |
| US-03 | Data Analyst | to build fact and dimension tables from staging data | the model supports fast, business-friendly querying | 5 | 1 |

**Definition of Done:** Star schema deployed in Snowflake; row counts reconcile against source; data dictionary published.

---

## Epic 2: Data Quality & Standardisation

**Goal:** Make the data trustworthy before anyone builds a report on top of it.

| Story | As a... | I want... | So that... | Points | Sprint |
|---|---|---|---|---|---|
| US-04 | Data Analyst | to integrate a live FX rate API | transactions in different currencies can be compared on a like-for-like basis | 5 | 2 |
| US-05 | Customer Insights Manager | all transaction amounts standardised to GBP | I can compare customer spend without manually converting currencies | 3 | 2 |
| US-06 | Data Analyst | an automated data quality check (nulls, duplicates, invalid dates, negative amounts) | issues are caught before they reach reporting, not after | 8 | 2 |
| US-07 | Data & Analytics Lead | a data quality log produced on every run | I can see what was excluded/fixed and why, for audit purposes | 3 | 2 |

**Definition of Done:** QA script runs end-to-end and produces a logged, reviewable output; no silent data loss.

---

## Epic 3: Analysis & Self-Service Enablement

**Goal:** Turn the trusted model into answers stakeholders can actually use.

| Story | As a... | I want... | So that... | Points | Sprint |
|---|---|---|---|---|---|
| US-08 | Product Manager | to see spend by category and channel | I can identify which products/channels drive engagement | 5 | 3 |
| US-09 | Customer Insights Manager | customer segments based on spend behaviour | marketing can target offers appropriately | 5 | 3 |
| US-10 | Product Manager | secure, read-only access to summary views only (not raw customer data) | I get the insight I need without a data privacy risk | 5 | 3 |
| US-11 | Data Analyst | to document every output against the original business requirement | there's full traceability from ask to answer | 2 | 3 |

**Definition of Done:** Views published in Snowflake; sample stakeholder walkthrough completed; traceability matrix signed off.

---

## Sprint Summary

| Sprint | Focus | Points Committed | Points Delivered |
|---|---|---|---|
| Sprint 1 | Data modelling & ingestion | 13 | 13 |
| Sprint 2 | Data quality & FX standardisation | 19 | 19 |
| Sprint 3 | Analysis & secure sharing | 17 | 17 |

**Retrospective note (Sprint 2):** Data quality checks surfaced more duplicate transactions than expected (~3% of records). Added an extra validation step rather than cutting scope — flagged to stakeholder as a process improvement for the source system, not just a one-off fix.
