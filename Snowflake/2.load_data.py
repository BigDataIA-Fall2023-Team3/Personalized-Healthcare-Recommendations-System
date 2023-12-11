
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

# Define the list of dataset names, corresponding stage names, and file URLs
dataset_mapping = [
    {'stage_name': 'DOCTORS_STAGE', 'table_name': 'DOCTORS', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Doctors.csv',
     'columns': ['DOCTORS_ID VARCHAR(16777216)', 'LICENSE_ID VARCHAR(16777216)', 'DOCTORS_NAME VARCHAR(16777216)', 'DEGREE VARCHAR(16777216)', 'INSURANCE VARCHAR(16777216)']},
    {'stage_name': 'HOSPITAL_AFFILICATIONS_STAGE', 'table_name': 'HOSPITAL_AFFILICATIONS', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Hospital Affilications.csv',
     'columns': ['ID VARCHAR(16777216)', 'DOCTORS_ID VARCHAR(16777216)', 'HOSPITAL_AFFILICATIONS VARCHAR(16777216)']},
    {'stage_name': 'HOSPITALS_STAGE', 'table_name': 'HOSPITALS', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Hospitals.csv',
     'columns': ['DOCTORS_ID VARCHAR(16777216)', 'HOSPITAL_ID VARCHAR(16777216)', 'ZIPCODE VARCHAR(16777216)']},
    {'stage_name': 'MASTER_DATASET_STAGE', 'table_name': 'MASTER_DATASET', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Master Dataset.csv',
     'columns': ['LICENSE_NUMBER VARCHAR(16777216)', 'DOCTORS_NAME VARCHAR(16777216)', 'LICENSE_TYPE VARCHAR(16777216)',
                 'LICENSE_STATUS VARCHAR(16777216)', 'DEGREE VARCHAR(16777216)', 'ACCEPTS_MEDICAID VARCHAR(16777216)',
                 'ACCEPTS_NEW_PATIENTS VARCHAR(16777216)', 'PRACTICE_SPECIALITY VARCHAR(16777216)',
                 'HOSPITAL_AFFILIATIONS VARCHAR(16777216)', 'INSURANCE_PLANS VARCHAR(16777216)', 'CITY VARCHAR(16777216)',
                 'STATE VARCHAR(16777216)', 'ZIPCODE VARCHAR(16777216)']},
    {'stage_name': 'PINCODE_STATE_CITY_STAGE', 'table_name': 'PINCODE_STATE_CITY', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Pincodes_State_City.csv',
     'columns': ['HOSPITAL_ID VARCHAR(16777216)', 'CITY VARCHAR(16777216)', 'STATE VARCHAR(16777216)', 'ZIPCODE VARCHAR(16777216)']},
    {'stage_name': 'PRACTICE_SPECIALITIES_STAGE', 'table_name': 'PRACTICE_SPECIALITIES', 'file_url': 's3://final-project-datasets-1/Datasets-1-csv/Practice Specialities.csv',
     'columns': ['DOCTOR_ID VARCHAR(16777216)', 'PRACTICE_SPECIALITIES VARCHAR(16777216)']}
]


# Initialize Snowflake connection
conn = snowflake.connector.connect(**snowflake_params)

# Loop through the dataset mappings and create stages, tables, and copy data dynamically
for mapping in dataset_mapping:
    stage_name = mapping['stage_name']
    table_name = mapping['table_name']
    file_url = mapping['file_url']
    columns = ',\n'.join(mapping['columns'])  # Join columns with newline

    # Create an external stage to reference the public S3 bucket
    create_stage_sql = f"CREATE OR REPLACE STAGE FP_DB.DATASETS_1.{stage_name} URL = '{file_url}'"
    conn.cursor().execute(create_stage_sql)

    # Create a table in the datasets_1 schema to store the data
    create_table_sql = f"CREATE OR REPLACE TABLE FP_DB.DATASETS_1.{table_name} (\n{columns}\n)"
    conn.cursor().execute(create_table_sql)

    # Copy data from the stage into the table, handling errors
    copy_data_sql = f"COPY INTO FP_DB.DATASETS_1.{table_name} FROM @FP_DB.DATASETS_1.{stage_name} FILE_FORMAT = (TYPE = 'CSV') ON_ERROR = 'CONTINUE'"
    conn.cursor().execute(copy_data_sql)

    # Grant necessary privileges to the ANALYST_ROLE on the table
    grant_privileges_sql = f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE FP_DB.DATASETS_1.{table_name} TO ROLE ANALYST_ROLE"
    conn.cursor().execute(grant_privileges_sql)

# Close the Snowflake connection
conn.close()
