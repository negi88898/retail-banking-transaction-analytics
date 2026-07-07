# Executive Summary: Retail Banking Transaction Analytics Platform

**To:** Head of Customer Insights
**From:** [Your Name], Data & Analytics Analyst
**Re:** Delivery of trusted transaction data model and initial findings

## What Was Delivered

A single, trusted view of customer transaction data — consolidated from previously fragmented multi-channel extracts into a Snowflake data model, with automated currency standardisation and a documented data quality framework. This directly addresses the gap flagged in our initial scoping: the team previously had no reliable way to compare customer spend across currencies or trust that reported figures were free of duplicates and data entry errors.

## What We Found

- **94.9% of raw transaction data passed quality checks cleanly.** The remaining 5.1% (628 of 12,360 rows) broke down into duplicates (360), broken customer references (116), invalid dates (58), unexpected negative amounts (59), and currency conversion failures (35) — each logged individually rather than silently dropped.
- **Travel is our highest-spend category** (£479K), followed by general/other transactions (£285K) and Shopping & Retail (£241K).
- **Customer spend is concentrated**: our "Premium" segment (27 customers) averages £5,580 in spend, over 3x the "Moderate" segment average.
- **Channel usage varies meaningfully by customer segment** — worth a deeper look before any channel-specific product decisions are made.

## Recommendation

1. **Adopt this model as the source of truth** for customer spend reporting going forward, replacing manual spreadsheet reconciliation.
2. **Flag the duplicate-transaction rate (2.9% of raw data) to the source system owner** — this is a pattern worth investigating at the point of ingestion, not just cleaning up downstream every time.
3. **Share aggregated views with the Product team** via the secure, PII-free view already built (`VW_PRODUCT_TEAM_SECURE_SHARE`) — no data duplication, no privacy risk, and no manual export process required.
4. **Revisit customer segmentation thresholds next quarter** once a full 12 months of clean data is available, to make sure segment boundaries reflect actual behaviour rather than an initial estimate.

## Next Steps

- Schedule a walkthrough with Product and Marketing to confirm the self-service views meet their needs.
- Agree a refresh cadence (recommend daily batch, matching the source extract).
- Scope Phase 2: predictive churn/engagement scoring on top of this now-trusted data model.

*Full technical documentation, requirements traceability, and reproducible code available in the accompanying repository.*
