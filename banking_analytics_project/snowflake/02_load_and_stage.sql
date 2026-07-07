-- ============================================================
-- Load Data into Snowflake: RAW layer, then MODELLED layer
-- ============================================================

USE DATABASE BANKING_ANALYTICS;
USE WAREHOUSE BANKING_ANALYTICS_WH;

-- ---------------------------------------------------------
-- STEP 1: Upload files to the stage
-- ---------------------------------------------------------
-- Via Snowsight UI: Data > Databases > BANKING_ANALYTICS > RAW >
--   Stages > BANKING_STAGE > "+ Files" and upload:
--     data/raw_customers.csv
--     data/raw_categories.csv
--     data/raw_transactions.csv
--     data/customers_enriched.csv
--     data/transactions_clean.csv
--
-- Or via SnowSQL CLI:
--   PUT file:///path/to/data/raw_transactions.csv @RAW.BANKING_STAGE;
--   (repeat for each file)

LIST @RAW.BANKING_STAGE;

-- ---------------------------------------------------------
-- STEP 2: Load RAW layer (unmodified, for audit trail)
-- ---------------------------------------------------------
USE SCHEMA RAW;

COPY INTO RAW_TRANSACTIONS
FROM @BANKING_STAGE/raw_transactions.csv
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
ON_ERROR = 'CONTINUE';

COPY INTO RAW_CUSTOMERS
FROM @BANKING_STAGE/raw_customers.csv
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
ON_ERROR = 'CONTINUE';

COPY INTO RAW_CATEGORIES
FROM @BANKING_STAGE/raw_categories.csv
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
ON_ERROR = 'CONTINUE';

-- Reconciliation check: row counts should match source CSVs exactly
SELECT 'RAW_TRANSACTIONS' AS table_name, COUNT(*) AS row_count FROM RAW_TRANSACTIONS
UNION ALL
SELECT 'RAW_CUSTOMERS', COUNT(*) FROM RAW_CUSTOMERS
UNION ALL
SELECT 'RAW_CATEGORIES', COUNT(*) FROM RAW_CATEGORIES;

-- ---------------------------------------------------------
-- STEP 3: Load MODELLED layer (quality-checked, from Python outputs)
-- ---------------------------------------------------------
USE SCHEMA MODELLED;

COPY INTO DIM_CUSTOMER
FROM @RAW.BANKING_STAGE/customers_enriched.csv
FILE_FORMAT = (FORMAT_NAME = 'RAW.CSV_FORMAT')
ON_ERROR = 'CONTINUE'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

COPY INTO DIM_CATEGORY
FROM @RAW.BANKING_STAGE/raw_categories.csv
FILE_FORMAT = (FORMAT_NAME = 'RAW.CSV_FORMAT')
ON_ERROR = 'CONTINUE';

COPY INTO FACT_TRANSACTIONS
FROM @RAW.BANKING_STAGE/transactions_clean.csv
FILE_FORMAT = (FORMAT_NAME = 'RAW.CSV_FORMAT')
ON_ERROR = 'CONTINUE'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Populate DIM_DATE from the distinct dates seen in the fact table
-- (a lightweight alternative to a generated calendar table)
INSERT INTO DIM_DATE
SELECT DISTINCT
    transaction_date                                   AS date_key,
    YEAR(transaction_date)                              AS year_num,
    MONTH(transaction_date)                             AS month_num,
    MONTHNAME(transaction_date)                          AS month_name,
    QUARTER(transaction_date)                            AS quarter_num,
    DAYNAME(transaction_date)                            AS day_of_week
FROM FACT_TRANSACTIONS
WHERE transaction_date IS NOT NULL;

-- ---------------------------------------------------------
-- STEP 4: Post-load validation (REQ-01 acceptance criteria)
-- ---------------------------------------------------------
SELECT 'FACT_TRANSACTIONS' AS table_name, COUNT(*) AS row_count FROM FACT_TRANSACTIONS
UNION ALL
SELECT 'DIM_CUSTOMER', COUNT(*) FROM DIM_CUSTOMER
UNION ALL
SELECT 'DIM_CATEGORY', COUNT(*) FROM DIM_CATEGORY
UNION ALL
SELECT 'DIM_DATE', COUNT(*) FROM DIM_DATE;

-- Referential integrity check - every fact row should join to a valid customer
SELECT COUNT(*) AS orphaned_transactions
FROM FACT_TRANSACTIONS f
LEFT JOIN DIM_CUSTOMER c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
