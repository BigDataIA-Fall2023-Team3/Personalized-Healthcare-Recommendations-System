
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from bs4 import BeautifulSoup
from airflow.utils.dates import days_ago

import requests
import pandas as pd
import re


# Specify the default arguments for the DAG
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'start_date': datetime(2023, 1, 1),
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# Instantiate the DAG
dag = DAG(
     # Set the desired schedule interval
    dag_id="wikipedia_scraper",
    schedule_interval=None,   # Use schedule_interval instead of schedule
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["data_scraping"],
)

# Define a function that will be executed by the PythonOperator
def scrape_and_download():
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

# Lets now iterate through the head HTML code and make list of clean headings

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


# Reformat the data to fit the tables of the database schema
# Modifying any column's character limit in the dataframe

#reformatting 'Infectious agent' column by limitting the character length to 132 characters
        df['Infectious agent'] = df['Infectious agent'].str[:132]
#reformatting 'Vaccine(s)' column to take in only 14 character long values
        df['Vaccine(s)'] = df['Vaccine(s)'].str[:14]




#
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
        df3.to_csv('/opt/airflow/List_of_Infectious_Diseases.csv', index=False, encoding='utf-8')

        print(df3)
    # Save the scraped data to a CSV file

# Create a PythonOperator that will run the scrape_and_download function
scrape_task = PythonOperator(
    task_id='scrape_and_download',
    python_callable=scrape_and_download,
    dag=dag,
)

# Set the task dependencies
scrape_task

if __name__ == "__main__":
    dag.cli()
