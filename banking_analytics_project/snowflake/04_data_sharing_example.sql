-- ============================================================
-- Secure Data Sharing: Product Team Access
-- Satisfies REQ-06: share summary-level data with the Product
-- team without duplicating data or exposing customer PII.
--
-- Pattern used: Secure View + (in a real multi-account setup) a
-- Snowflake Share object. Secure Views hide the underlying query
-- logic and base table structure from consumers - appropriate
-- when sharing outside the immediate team.
-- ============================================================

USE DATABASE BANKING_ANALYTICS;
USE SCHEMA MODELLED;
USE WAREHOUSE BANKING_ANALYTICS_WH;

-- ---------------------------------------------------------
-- STEP 1: Create a Secure View exposing only aggregated,
-- non-identifiable data - no customer_id, no names, no DOB.
-- ---------------------------------------------------------
CREATE OR REPLACE SECURE VIEW VW_PRODUCT_TEAM_SECURE_SHARE AS
SELECT
    cat.category_name,
    f.channel,
    d.year_num,
    d.month_num,
    c.segment,
    c.region,
    COUNT(*)                        AS transaction_count,
    ROUND(SUM(f.amount_gbp), 2)      AS total_spend_gbp,
    ROUND(AVG(f.amount_gbp), 2)      AS avg_transaction_gbp,
    COUNT(DISTINCT f.customer_id)    AS distinct_customers   -- count only, not IDs
FROM FACT_TRANSACTIONS f
JOIN DIM_CATEGORY cat ON f.category_id = cat.category_id
JOIN DIM_DATE d ON f.transaction_date = d.date_key
JOIN DIM_CUSTOMER c ON f.customer_id = c.customer_id
GROUP BY cat.category_name, f.channel, d.year_num, d.month_num, c.segment, c.region;

COMMENT ON VIEW VW_PRODUCT_TEAM_SECURE_SHARE IS
    'Aggregated, PII-free view for Product team consumption. No customer_id, '
    'name, or DOB exposed - satisfies data minimisation principle for REQ-06.';

-- Verify no row-level PII leaks through
SELECT * FROM VW_PRODUCT_TEAM_SECURE_SHARE LIMIT 10;


-- ---------------------------------------------------------
-- STEP 2: Create a dedicated read-only role for the Product team
-- Principle of least privilege - they get SELECT on the secure
-- view only, not on any base table in MODELLED or RAW.
-- ---------------------------------------------------------
CREATE ROLE IF NOT EXISTS PRODUCT_TEAM_READONLY;

GRANT USAGE ON DATABASE BANKING_ANALYTICS TO ROLE PRODUCT_TEAM_READONLY;
GRANT USAGE ON SCHEMA MODELLED TO ROLE PRODUCT_TEAM_READONLY;
GRANT SELECT ON VIEW VW_PRODUCT_TEAM_SECURE_SHARE TO ROLE PRODUCT_TEAM_READONLY;
GRANT USAGE ON WAREHOUSE BANKING_ANALYTICS_WH TO ROLE PRODUCT_TEAM_READONLY;

-- Explicitly confirm base tables are NOT granted to this role
-- (no GRANT SELECT ON FACT_TRANSACTIONS / DIM_CUSTOMER to PRODUCT_TEAM_READONLY)


-- ---------------------------------------------------------
-- STEP 3 (reference only): Cross-account sharing pattern
-- If the Product team sits in a separate Snowflake account
-- (common in larger organisations), the equivalent pattern is
-- a Snowflake SHARE object rather than a role grant:
-- ---------------------------------------------------------
-- CREATE SHARE PRODUCT_TEAM_SHARE;
-- GRANT USAGE ON DATABASE BANKING_ANALYTICS TO SHARE PRODUCT_TEAM_SHARE;
-- GRANT USAGE ON SCHEMA MODELLED TO SHARE PRODUCT_TEAM_SHARE;
-- GRANT SELECT ON VIEW VW_PRODUCT_TEAM_SECURE_SHARE TO SHARE PRODUCT_TEAM_SHARE;
-- ALTER SHARE PRODUCT_TEAM_SHARE ADD ACCOUNTS = <consumer_account_identifier>;
--
-- This avoids copying data across accounts entirely - the consumer
-- queries live data with zero duplication and zero ETL to maintain.
