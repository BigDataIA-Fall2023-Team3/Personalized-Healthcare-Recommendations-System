import pandas as pd
import boto3
from io import BytesIO

# AWS S3 configurations
s3_bucket_name = 'final-project-datasets-1'
s3_folder_name = 'Datasets-1-csv'

# Initialize S3 client with anonymous credentials
s3_client = boto3.client('s3', aws_access_key_id="None", aws_secret_access_key="None")

# File paths
xlsx_file_paths = [
    "s3://final-project-datasets-1/Datasets-1/Doctors.xlsx",
    "s3://final-project-datasets-1/Datasets-1/Hospital Affilications.xlsx",
    "s3://final-project-datasets-1/Datasets-1/Hospitals.xlsx",
    "s3://final-project-datasets-1/Datasets-1/Master Dataset.xlsx",
    "s3://final-project-datasets-1/Datasets-1/Pincodes_State_City.xlsx",
    "s3://final-project-datasets-1/Datasets-1/Practice Specialities.xlsx"
]

# Loop through each XLSX file path, convert to CSV, and upload to S3
for xlsx_file_path in xlsx_file_paths:
    try:
        # Load XLSX data into a DataFrame
        df = pd.read_excel(xlsx_file_path)
        
        # Convert DataFrame to CSV format
        csv_data = df.to_csv(index=False, sep=';').encode('utf-8')

        # Define the S3 CSV file path
        csv_file_path = f"{s3_folder_name}/{xlsx_file_path.split('/')[-1].replace('.xlsx', '.csv')}"
        
        # Upload the CSV data to S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=csv_file_path,
            Body=csv_data,
            ContentType='text/csv'
        )
        
        print(f"Conversion and upload successful for {xlsx_file_path}")
    except Exception as e:
        print(f"Error processing {xlsx_file_path}: {str(e)}")



