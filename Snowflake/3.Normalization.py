
import snowflake.connector

# Snowflake connection parameters
snowflake_params = {
    "account": "QBAHNTM-QOB86779",
    "user": "sanjana",
    "password": "Sanju1209",
    "warehouse": "FP_WH",
    "database": "FP_DB",
    "schema": "DATASETS_1",
    "role": "ANALYST_ROLE"
}


# Initialize Snowflake connection
conn = snowflake.connector.connect(**snowflake_params)

############################################################################################################
create_udf_sql_1 = '''
CREATE OR REPLACE FUNCTION NORMALIZE_DEGREE(DEGREE VARCHAR)
  RETURNS VARCHAR
  LANGUAGE SQL
  AS
  '
  CASE
    WHEN DEGREE = ''M.D. or M.D. Equivalent'' THEN ''M.D''
    ELSE DEGREE
  END
  '
'''



############################################################################################################
create_table_sql_1 = '''
CREATE OR REPLACE TABLE FP_DB.DATASETS_2."DEGREE TABLE - POST NORMALIZATION" AS
SELECT DOCTORS_ID AS DOCTOR_ID,
       NORMALIZE_DEGREE(DEGREE) AS Degree
FROM FP_DB.DATASETS_1.DOCTORS
'''

conn.cursor().execute(create_table_sql_1)

create_table_sql_2 = '''
CREATE OR REPLACE TABLE FP_DB.DATASETS_2."PRACTICE SPECIALITIES" AS
WITH SplitValues AS (
    SELECT DOCTOR_ID,
           TRIM(VALUE::STRING) AS PRACTICE_SPECIALITIES
    FROM FP_DB.DATASETS_1.PRACTICE_SPECIALITIES,
         LATERAL FLATTEN(INPUT => SPLIT(PRACTICE_SPECIALITIES, ',')) AS VALUE
)
SELECT DOCTOR_ID, PRACTICE_SPECIALITIES
FROM SplitValues
'''

conn.cursor().execute(create_table_sql_2)

# Close the Snowflake connection
conn.close()
