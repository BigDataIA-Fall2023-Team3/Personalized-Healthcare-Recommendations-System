
import snowflake.connector
import os

# Snowflake connection parameters
snowflake_params = {
    "account": os.environ.get('SNOWFLAKE_ACCOUNT'),
    "user": os.environ.get('SNOWFLAKE_USER'),
    "password": os.environ.get('SNOWFLAKE_PASSWORD'),
    "warehouse": "FP_WH",
    "database": "FP_DB",
    "schema": "DATASETS_1",
    "role": "ANALYST_ROLE"
}


# Initialize Snowflake connection
conn = snowflake.connector.connect(**snowflake_params)

############################################################################################################
#Cleaning and Formatting the DOCTORS data

sql_query = """
CREATE OR REPLACE TABLE FP_DB.DATASETS_2.DOCTORS AS
SELECT
    D.DOCTORS_ID,
    D.DOCTORS_NAME AS DOCTORS_NAME,
    D.LICENSE_ID,
    M.LICENSE_STATUS,
    M.ACCEPTS_MEDICAID,
    M.ACCEPTS_NEW_PATIENTS,
    D.INSURANCE AS INSURANCE,
    M.CITY AS CITY,
    M.STATE AS STATE,
    LEFT(M.ZIPCODE, 5) AS ZIPCODE,
    Z.LATITUDE,
    Z.LONGITUDE,
    Z.TIMEZONE
FROM DATASETS_1.MASTER_DATASET AS M
FULL OUTER JOIN DATASETS_1.DOCTORS AS D ON M.LICENSE_NUMBER = D.LICENSE_ID
LEFT JOIN DATASETS_1.ZIPCODE AS Z ON LEFT(M.ZIPCODE, 5) = LEFT(LPAD(Z.ZIPCODE, 5, '0'), 5)
WHERE D.DOCTORS_ID IS NOT NULL AND D.DOCTORS_NAME IS NOT NULL;
"""
conn.cursor().execute(sql_query)
print("DOCTORS table created")

sql_query = """
CREATE OR REPLACE TABLE FP_DB.DATASETS_2.DOCTORS AS
SELECT 
    D.DOCTORS_ID,
    D.DOCTORS_NAME,
    D.LICENSE_ID,
    D.LICENSE_STATUS,
    D.ACCEPTS_MEDICAID,
    D.ACCEPTS_NEW_PATIENTS,
    S.VALUE::STRING AS INSURANCE,
    D.CITY,
    D.STATE,
    D.ZIPCODE,
    D.LATITUDE,
    D.LONGITUDE,
    D.TIMEZONE
FROM FP_DB.DATASETS_2.DOCTORS D,
LATERAL SPLIT_TO_TABLE(D.INSURANCE, ',') S;
"""

conn.cursor().execute(sql_query)
print("DOCTORS_INSURANCE table created")
############################################################################################################
# Cleaning and Formatting the Specialities data

sql_query = """
-- Create or replace the "PRACTISE_SPECIALITIES" table in "DATASETS_2"
CREATE OR REPLACE TABLE FP_DB.DATASETS_2.PRACTICE_SPECIALITIES AS
SELECT DISTINCT
    P.DOCTOR_ID,
    S.VALUE::STRING AS SPECIALITY
FROM FP_DB.DATASETS_1.PRACTICE_SPECIALITIES P,
LATERAL SPLIT_TO_TABLE(P.PRACTICE_SPECIALITIES, ',') S;
"""
conn.cursor().execute(sql_query)
print("PRACTISE_SPECIALITIES table created")

############################################################################################################
# Cleaning and Formatting the Hospital data

sql_query = """
-- Create or replace the "HOSPITALS" table in "DATASETS_2"
CREATE OR REPLACE TABLE FP_DB.DATASETS_2.HOSPITALS AS
WITH HospitalAffiliations AS (
    SELECT DISTINCT
        D.DOCTORS_ID,
        H.VALUE::STRING AS HOSPITAL_NAME
    FROM FP_DB.DATASETS_1.HOSPITAL_AFFILICATIONS D,
    LATERAL SPLIT_TO_TABLE(D.HOSPITAL_AFFILICATIONS, ',') H
)
SELECT 
    HA.DOCTORS_ID,
    HA.HOSPITAL_NAME,
    D.ZIPCODE,
    D.CITY,
    D.LATITUDE,
    D.LONGITUDE,
    D.TIMEZONE
FROM HospitalAffiliations HA
LEFT JOIN FP_DB.DATASETS_2.DOCTORS D ON HA.DOCTORS_ID = D.DOCTORS_ID
"""
conn.cursor().execute(sql_query)
print("HOSPITALS table created")

############################################################################################################
# Cleaning and Formatting the ZIPCODE data

sql_query = """
-- Create or replace the "ZIPCODE" table in "DATASETS_2"
CREATE OR REPLACE TABLE FP_DB.DATASETS_2.ZIPCODE AS
SELECT 
LPAD(CAST(ZIPCODE AS VARCHAR), 5, '0') AS ZIPCODE,
CITY,
STATE,
COUNTY,
LATITUDE,
LONGITUDE,
TIMEZONE
FROM FP_DB.DATASETS_1.ZIPCODE;
"""
conn.cursor().execute(sql_query)
print("ZIPCODE table created")



conn.close()
