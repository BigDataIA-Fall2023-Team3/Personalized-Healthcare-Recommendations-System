import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from bs4 import BeautifulSoup
from airflow.utils.dates import days_ago
import openai
import requests
import pandas as pd
import re
import boto3
import pinecone
import time
from openai import OpenAI
import ast

s3_bucket = 'final-project-data-sources'
s3_object_key = 'List_of_Infectious_Diseases.csv'
EMBEDDING_MODEL = "text-embedding-ada-002"

try:
    pinecone.init(api_key=os.getenv('PINECONE'), environment='gcp-starter')
    index = pinecone.Index('bigdata')
    print("Pinecone initialization and index creation successful.")
except Exception as e:
    print("An error occurred:", str(e))

# Instantiate the DAG


# Define a function that will be executed by the PythonOperator
def scrape_and_download(output_csv_file):
    # Site URL
    url = "https://en.wikipedia.org/wiki/List_of_infectious_diseases"

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse HTML code for the entire site
    soup = BeautifulSoup(html_content, "html.parser")

    # Your scraping code here
    dis = soup.find_all("table", attrs={"class": "sortable"})
#print("Number of tables on site: ",len(dis))

# Lets go ahead and scrape first table with HTML code dis[0]
    table1 = dis[0]

# the head will form our column names
    body = table1.find_all("tr")

# Head values (Column names) are the first items of the body list
    head = body[0] # 0th item is the header row

    body_rows = body[1:] # All other items becomes the rest of the rows



# Declare empty list to keep Columns names
    headings = []

    for item in head.find_all("th"): # loop through all th elements
    # convert the th elements to text and strip "\n"
        item = (item.text).rstrip("\n")
    # append the clean column name to headings
        headings.append(item)



    all_rows = [] # will be a list for list for all rows

    for row_num in range(len(body_rows)): # A row at a time
        row = [] # this will old entries for one row
        for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
        # row_item.text removes the tags from the entries
        # the following regex is to remove \xa0 and \n and comma from row_item.text
        # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
            aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
        #append aa to row - note one row entry is being appended
            row.append(aa)
    # append one row to all_rows
        all_rows.append(row)

# We can now use the data on all_rows and headings to make a table
# all_rows becomes our data and headings the column names
        df = pd.DataFrame(data=all_rows,columns=headings)
#shows the first few rows as a preview in the dataframe
#print(df)


#reformatting 'Infectious agent' column by limitting the character length to 132 characters
        df['Infectious agent'] = df['Infectious agent'].str[:132]
#reformatting 'Vaccine(s)' column to take in only 14 character long values
        df['Vaccine(s)'] = df['Vaccine(s)'].str[:14]

# #Cleaing all these columns' values to see if data is getting modified/replaced.
# #UPDATE: commenting below logic since, clean was successful.
        df['Infectious agent'] = df['Infectious agent'].str.replace('á','a')
        df['Infectious agent'] = df['Infectious agent'].str.replace(';','')
        df['Infectious agent'] = df['Infectious agent'].str.replace('Yes','NA')
        df['Infectious agent'] = df['Infectious agent'].str.replace(r'[41]','')
        df['Infectious agent'] = df['Infectious agent'].str.replace('usually','')
        df['Infectious agent'] = df['Infectious agent'].str.replace(r'[','')
        df['Infectious agent'] = df['Infectious agent'].str.replace(r']','')
        df['Common name'] = df['Common name'].str.replace(';','')
        df['Common name'] = df['Common name'].str.replace('–','')
        df['Common name'] = df['Common name'].str.replace('ä','a')
        df['Common name'] = df['Common name'].str.replace('’','')
        df[['Common name','Signs and symptoms','Diagnosis','Treatment','Vaccine(s)']] = df[['Common name','Signs and symptoms','Diagnosis','Treatment','Vaccine(s)']].fillna('NA') #yes it works
        df['Signs and symptoms'] = df['Signs and symptoms'].str.replace('–',' to ')
        df['Signs and symptoms'] = df['Signs and symptoms'].str.replace('ó','o')
        df['Signs and symptoms'] = df['Signs and symptoms'].str.replace('°',' degrees ')

# #inserting NaN values in the cells wherever empty
        import numpy as np
        df2 = df.replace(r'^\s*$', np.nan, regex=True)

#Now "df2" is my variable that stores updated dataframe having NaN values
#Using df2, I am replacing NaN values with appropriate data under symptoms column

        df2[['Signs and symptoms']] = df2[['Signs and symptoms']].fillna('No symptoms found')

    #Now "df2" is my variable that stores updated dataframe having NaN values
    #Using df2, I am replacing NaN values with appropriate data under diagnosis column

        df2[['Diagnosis']] = df2[['Diagnosis']].fillna('No diagnosis found')

    #Now "df2" is my variable that stores updated dataframe having NaN values
    #Using df2, I am replacing NaN values with appropriate data under treatment column

        df2[['Treatment']] = df2[['Treatment']].fillna('No treatment found')

    #renaming "Vaccine(s)" column as "Vaccine availability"
        df2 = df2.rename(columns={'Vaccine(s)': 'Vaccine_availability'})



# #renaming all columns into different names
        df2 = df2.rename(columns={'Infectious agent': 'Disease_agent'})
        df2 = df2.rename(columns={'Common name': 'Disease_name'})
        df2 = df2.rename(columns={'Signs and symptoms': 'Signs_and_symptoms'})


    #
    #creating a new dataframe df3 to only specify some columns in my diseases table
        df3 = df2[['Disease_name','Signs_and_symptoms','Diagnosis','Treatment']]


    #adding a new column to diseases table "Disease_Id"
        df3.insert(0, 'Disease_Id', range(1, 1 + len(df3)))

    # #Data cleaning is done for Diseases table
    # #Now exporting diseases dataframe in CSV
        # df3.to_csv('/opt/airflow/List_of_Infectious_Diseases.csv', index=False, encoding='utf-8')

    df3.to_csv(output_csv_file, index=True)
    upload_csv_to_s3(output_csv_file, 'List_of_Infectious_Diseases.csv')

#uploading to s3
       
def upload_csv_to_s3(csv_file_path, s3_object_key):
    a_key = os.getenv('A_KEY')
    sa_key = os.getenv('SA_KEY')

    # Configure AWS credentials
    os.environ['AWS_ACCESS_KEY_ID'] = a_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = sa_key

    s3_client = boto3.client('s3')

    # Upload the CSV file, replacing it if it already exists.
    s3_client.upload_file(csv_file_path, 'final-project-data-sources', s3_object_key)

def download_file_from_s3( local_file_path = 'diseases.csv', bucket_name='final-project-data-sources',object_key = 'diseases.csv'):
    aws_access_key_id = os.getenv('A_KEY')
    aws_secret_access_key = os.getenv('SA_KEY')
    try:
        # Initialize an S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Download the file
        s3.download_file(bucket_name, object_key, local_file_path)
        print(f"File downloaded to {local_file_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")


def gen_embed(filename='diseases.csv'):
    df = pd.read_csv(filename)
    df = df.iloc[190:195]
    list = df['Signs_and_symptoms'].tolist()
    client = OpenAI(api_key=os.getenv('OPENAI_API'))
    print("______________________________________________here")
    print(len(list))
    
    embed_list = []
    c = 0
    for i in list:
        text_embedding_response = client.embeddings.create(
             input=i,
            model=EMBEDDING_MODEL,
        )
        c+=1
        text_embedding = text_embedding_response.data[0].embedding
        embed_list.append(text_embedding)
        print(c)
        time.sleep(20)
    df['embeds'] = embed_list
    df.to_csv("embeddings.csv", index=False)
    upload_csv_to_s3("embeddings.csv", "embeddings.csv")


def download_embeds( local_file_path, object_key = 'embeddings.csv', bucket_name='final-project-data-sources'):
    aws_access_key_id = os.getenv('A_KEY')
    aws_secret_access_key = os.getenv('SA_KEY')
    try:
        # Initialize an S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Download the file
        s3.download_file(bucket_name, object_key, local_file_path)
        print(f"File downloaded to {local_file_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")



def pinecone_upsert(filename='embeddings.csv'):
    df = pd.read_csv(filename)
    df['embeds'] = df['embeds'].apply(ast.literal_eval)
    df.head()

    df = df.rename(columns={df.columns[0]: 'Index'})
    df['Index'] = df['Index'].astype(str)
    # Setting batch size as 32
    batch_size = 32
    for i in range(0, len(df), batch_size):
        batch_df = df[i:i + batch_size]
        id_list = batch_df['Index'].tolist()
        embeds = batch_df['embeds'].tolist()
        diseases_list = batch_df['Disease_name'].tolist()
        symptoms_list = batch_df['Signs_and_symptoms'].tolist()
        treatment_list = batch_df['Treatment'].tolist()
        diagnosis_list = batch_df['Diagnosis'].tolist()
        m_list = []
        
        for i in range(len(id_list)):
            m = {'Disease_name': diseases_list[i], 'Signs_and_symptoms': symptoms_list[i], 'Treatment': treatment_list[i], 'Diagnosis': diagnosis_list[i]}
            m_list.append(m)
        print("___________________here")
        print(m_list)
        # meta = [{'text': text_batch} for text_batch in zip(metalist, text_list)]
        to_upsert = zip(id_list, embeds, m_list) 
        index.upsert(vectors=list(to_upsert))




dag = DAG(
     # Set the desired schedule interval
    dag_id="wikipedia_scraper",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["data_scraping"],
)


# Create a PythonOperator that will run the scrape_and_download function
scrape_task = PythonOperator(
    task_id='scrape_and_download',
    python_callable=scrape_and_download,
    op_args=['/opt/airflow/List_of_Infectious_Diseases.csv'],  # Provide the output CSV file path as an argument
    provide_context=True,  # This is needed to access the context in the function
    dag=dag,
)

# Set the task dependencies
scrape_task



dag2 = DAG(
     # Set the desired schedule interval
    dag_id="embeddings_generator",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
)

download_file = PythonOperator(
    task_id='download',
    python_callable=download_file_from_s3, 
    op_args=['/opt/airflow/diseases.csv'],
    provide_context=True,  
    dag=dag2,
)

generate_embeds = PythonOperator(
    task_id='gen_embed',
    python_callable=gen_embed,
    provide_context=True,  # This is needed to access the context in the function
    dag=dag2,
)

download_file >> generate_embeds

dag3 = DAG(
     # Set the desired schedule interval
    dag_id="add_to_pinecone",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
)

download = PythonOperator(
    task_id='download_embeds',
    python_callable=download_embeds, 
    op_args=['/opt/airflow/embeddings.csv','embeddings.csv'],
    provide_context=True,  
    dag=dag3,
)

pinecone_update = PythonOperator(
    task_id='update_pinecone',
    python_callable=pinecone_upsert, 
    provide_context=True,  
    dag=dag3,
)

download >> pinecone_update



