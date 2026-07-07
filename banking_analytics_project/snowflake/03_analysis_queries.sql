-- ============================================================
-- Retail Banking Transaction Analytics - Business Queries
-- Maps directly to REQ-04 and REQ-05 in the BRD.
-- ============================================================

USE DATABASE BANKING_ANALYTICS;
USE SCHEMA MODELLED;
USE WAREHOUSE BANKING_ANALYTICS_WH;


-- 1. SPEND BY CATEGORY AND CHANNEL (view for self-service use, REQ-05)
CREATE OR REPLACE VIEW VW_SPEND_BY_CATEGORY_CHANNEL AS
SELECT
    cat.category_name,
    f.channel,
    COUNT(*)                           AS transaction_count,
    ROUND(SUM(f.amount_gbp), 2)         AS total_spend_gbp,
    ROUND(AVG(f.amount_gbp), 2)         AS avg_transaction_gbp
FROM FACT_TRANSACTIONS f
JOIN DIM_CATEGORY cat ON f.category_id = cat.category_id
GROUP BY cat.category_name, f.channel;

SELECT * FROM VW_SPEND_BY_CATEGORY_CHANNEL
ORDER BY total_spend_gbp DESC;


-- 2. MONTHLY SPEND TRENDS
CREATE OR REPLACE VIEW VW_MONTHLY_TRENDS AS
SELECT
    d.year_num,
    d.month_num,
    d.month_name,
    COUNT(*)                       AS transaction_count,
    ROUND(SUM(f.amount_gbp), 2)     AS total_spend_gbp,
    COUNT(DISTINCT f.customer_id)   AS active_customers
FROM FACT_TRANSACTIONS f
JOIN DIM_DATE d ON f.transaction_date = d.date_key
GROUP BY d.year_num, d.month_num, d.month_name;

SELECT * FROM VW_MONTHLY_TRENDS
ORDER BY year_num, month_num;


-- 3. CUSTOMER SEGMENTATION SUMMARY (feeds US-09, Product/Marketing use case)
CREATE OR REPLACE VIEW VW_CUSTOMER_SEGMENTS AS
SELECT
    c.spend_segment,
    c.region,
    COUNT(DISTINCT c.customer_id)       AS customers,
    ROUND(AVG(c.total_spend_gbp), 2)     AS avg_customer_spend_gbp,
    ROUND(SUM(c.total_spend_gbp), 2)     AS total_segment_spend_gbp
FROM DIM_CUSTOMER c
GROUP BY c.spend_segment, c.region;

SELECT * FROM VW_CUSTOMER_SEGMENTS
ORDER BY total_segment_spend_gbp DESC;


-- 4. CHANNEL ADOPTION BY CUSTOMER SEGMENT
-- Business question: are Premier customers using mobile, or still branch-heavy?
SELECT
    c.segment,
    f.channel,
    COUNT(*)                                                       AS transactions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY c.segment), 1) AS pct_of_segment_transactions
FROM FACT_TRANSACTIONS f
JOIN DIM_CUSTOMER c ON f.customer_id = c.customer_id
GROUP BY c.segment, f.channel
ORDER BY c.segment, transactions DESC;


-- 5. TOP 20 HIGHEST-SPENDING CUSTOMERS (using QUALIFY - Snowflake native)
SELECT
    c.customer_id,
    c.region,
    c.segment,
    c.total_spend_gbp,
    RANK() OVER (ORDER BY c.total_spend_gbp DESC) AS spend_rank
FROM DIM_CUSTOMER c
QUALIFY spend_rank <= 20
ORDER BY spend_rank;


-- 6. DATA QUALITY MONITORING QUERY
-- Business question: what % of raw transactions made it through QA cleanly?
-- (cross-references RAW vs MODELLED row counts - a repeatable health check)
SELECT
    (SELECT COUNT(*) FROM RAW.RAW_TRANSACTIONS)     AS raw_row_count,
    (SELECT COUNT(*) FROM FACT_TRANSACTIONS)        AS clean_row_count,
    ROUND(100.0 * (SELECT COUNT(*) FROM FACT_TRANSACTIONS) /
          (SELECT COUNT(*) FROM RAW.RAW_TRANSACTIONS), 2) AS pass_rate_pct;


-- 7. DORMANT / AT-RISK ACCOUNTS
-- Business question: which customers haven't transacted in 90+ days?
-- (useful proactive-outreach output, similar spirit to churn analysis)
SELECT
    c.customer_id,
    c.region,
    c.segment,
    MAX(f.transaction_date)                      AS last_transaction_date,
    DATEDIFF('day', MAX(f.transaction_date), CURRENT_DATE()) AS days_since_last_transaction
FROM DIM_CUSTOMER c
JOIN FACT_TRANSACTIONS f ON c.customer_id = f.customer_id
GROUP BY c.customer_id, c.region, c.segment
HAVING days_since_last_transaction > 90
ORDER BY days_since_last_transaction DESC;
