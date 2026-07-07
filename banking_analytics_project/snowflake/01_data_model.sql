-- ============================================================
-- Retail Banking Transaction Analytics - Snowflake Data Model
-- Satisfies REQ-01: star schema design; demonstrates warehouse,
-- stage, and file format configuration.
-- ============================================================

-- 1. WAREHOUSE
CREATE WAREHOUSE IF NOT EXISTS BANKING_ANALYTICS_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute for retail banking transaction analytics project';

USE WAREHOUSE BANKING_ANALYTICS_WH;

-- 2. DATABASE + SCHEMAS
-- Separate RAW and MODELLED schemas: raw data is never overwritten in
-- place, preserving auditability (per BRD non-functional requirements).
CREATE DATABASE IF NOT EXISTS BANKING_ANALYTICS;
USE DATABASE BANKING_ANALYTICS;

CREATE SCHEMA IF NOT EXISTS RAW        COMMENT = 'Unmodified source extracts, staged as-is';
CREATE SCHEMA IF NOT EXISTS MODELLED   COMMENT = 'Clean, quality-checked star schema for analysis';

-- 3. FILE FORMAT + STAGE
CREATE OR REPLACE FILE_FORMAT RAW.CSV_FORMAT
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL', 'null', 'None')
    EMPTY_FIELD_AS_NULL = TRUE;

CREATE OR REPLACE STAGE RAW.BANKING_STAGE
    FILE_FORMAT = RAW.CSV_FORMAT
    COMMENT = 'Stage for uploading raw and cleaned CSV extracts';

-- ============================================================
-- 4. RAW LAYER — mirrors source files exactly (audit trail)
-- ============================================================
USE SCHEMA RAW;

CREATE OR REPLACE TABLE RAW_TRANSACTIONS (
    transaction_id      VARCHAR(20),
    customer_id         VARCHAR(20),
    category_id         VARCHAR(10),
    transaction_date    VARCHAR(20),   -- kept as text in raw layer; typed properly downstream
    amount               NUMBER(12,2),
    currency             VARCHAR(5),
    merchant             VARCHAR(100),
    channel              VARCHAR(30)
);

CREATE OR REPLACE TABLE RAW_CUSTOMERS (
    customer_id          VARCHAR(20),
    first_name            VARCHAR(50),
    last_name             VARCHAR(50),
    date_of_birth          DATE,
    region                VARCHAR(50),
    segment               VARCHAR(30),
    join_date              DATE
);

CREATE OR REPLACE TABLE RAW_CATEGORIES (
    category_id       VARCHAR(10),
    category_name      VARCHAR(50)
);

-- ============================================================
-- 5. MODELLED LAYER — star schema for analysis
-- ============================================================
USE SCHEMA MODELLED;

-- DIM_CUSTOMER
CREATE OR REPLACE TABLE DIM_CUSTOMER (
    customer_id        VARCHAR(20)  PRIMARY KEY,
    first_name          VARCHAR(50),
    last_name           VARCHAR(50),
    date_of_birth        DATE,
    region              VARCHAR(50),
    segment             VARCHAR(30),
    join_date            DATE,
    total_spend_gbp      NUMBER(12,2),
    spend_segment        VARCHAR(30)
)
COMMENT = 'Customer dimension enriched with spend-based segmentation (REQ-04)';

-- DIM_CATEGORY
CREATE OR REPLACE TABLE DIM_CATEGORY (
    category_id     VARCHAR(10)  PRIMARY KEY,
    category_name    VARCHAR(50)
);

-- DIM_DATE
CREATE OR REPLACE TABLE DIM_DATE (
    date_key          DATE  PRIMARY KEY,
    year_num           NUMBER(4,0),
    month_num          NUMBER(2,0),
    month_name         VARCHAR(20),
    quarter_num        NUMBER(1,0),
    day_of_week        VARCHAR(20)
);

-- FACT_TRANSACTIONS
CREATE OR REPLACE TABLE FACT_TRANSACTIONS (
    transaction_id     VARCHAR(20)  PRIMARY KEY,
    customer_id        VARCHAR(20)  REFERENCES DIM_CUSTOMER(customer_id),
    category_id        VARCHAR(10)  REFERENCES DIM_CATEGORY(category_id),
    transaction_date    DATE         REFERENCES DIM_DATE(date_key),
    amount               NUMBER(12,2),
    currency             VARCHAR(5),
    amount_gbp           NUMBER(12,2),
    merchant             VARCHAR(100),
    channel              VARCHAR(30)
)
COMMENT = 'Quality-checked, GBP-standardised transaction fact table (REQ-02, REQ-03)';

-- Next step: see 02_load_and_stage.sql
