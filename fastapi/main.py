from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from openai import OpenAI
client = OpenAI()
import snowflake.connector
import os
import pandas as pd
import math

app = FastAPI()

# Define a Pydantic model to accept patient symptoms
class SymptomModel(BaseModel):
    symptoms: str
    age: int
    gender: str
    special_instructions: str

# Define a Pydantic model to accept the OpenAI API key
class OpenAIModel(BaseModel):
    api_key: str

class Insurance(BaseModel):
    insurance: str
    specialty: str
    Zipcode: str

# Set your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']  # Replace with your actual API key
snowflake_config = {
    "user": os.environ['SNOWFLAKE_USER'],
    "password": os.environ['SNOWFLAKE_PASSWORD'],
    "account": os.environ['SNOWFLAKE_ACCOUNT'],
    "role": "ANALYST_ROLE",
    "database": "FP_DB",
    "warehouse": "FP_WH",
}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c   
    return distance

def find_close(l, myzip, insurance, specialty):
    d = {}
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM FP_DB.DATASETS_2.ZIPCODE")
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['ZipCode', 'City', 'State', 'County', 'Latitude', 'Longitude', 'TimeZone' ]
    
    result = df[df['ZipCode'] == myzip]
    if result.empty:
        return "Zip code not found."
    
    lat1 = float(result['Latitude'].iloc[0])
    long1 = float(result['Longitude'].iloc[0])
    
    for i in l:
        result = df[df['ZipCode'] == i]
        if not result.empty:
            latitude = float(result['Latitude'].iloc[0])
            longitude = float(result['Longitude'].iloc[0])
            dis = haversine(lat1, long1, latitude, longitude)
            d[i] = dis
    
    # Sort the dictionary by distance
    sorted_d = dict(sorted(d.items(), key=lambda item: item[1]))
    results = []
    for i in sorted_d.keys():
        cursor.execute("SELECT * FROM FP_DB.DATASETS_2.DOCTORS LEFT JOIN FP_DB.DATASETS_2.PRACTICE_SPECIALITIES ON DOCTORS.DOCTORS_ID = PRACTICE_SPECIALITIES.DOCTOR_ID WHERE SPECIALITY LIKE %s AND ZIPCODE = %s AND INSURANCE = %s;", (f'%{specialty}%', i, insurance))
        specialties = cursor.fetchall()
        if specialties:
            for i in specialties:
                results.append(i)
    return results[:3]


def find_close_hospital(zipcode):
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM FP_DB.DATASETS_2.HOSPITALS WHERE ZIPCODE = %s;", (zipcode))
    specialties = cursor.fetchall()
    return specialties
    




def get_doctor_specialties():
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT SPECIALITY FROM FP_DB.DATASETS_2.PRACTICE_SPECIALITIES;")
    specialties = [row[0] for row in cursor.fetchall()]
    # print(specialties)
    cursor.close()
    conn.close()
    return specialties

def get_doctor(specialty, insurance, Zipcode):
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    # Use placeholders for specialty and insurance variables
    cursor.execute("SELECT * FROM FP_DB.DATASETS_2.DOCTORS LEFT JOIN FP_DB.DATASETS_2.PRACTICE_SPECIALITIES ON DOCTORS.DOCTORS_ID = PRACTICE_SPECIALITIES.DOCTOR_ID WHERE speciality LIKE %s AND INSURANCE = %s;", (f'%{specialty}%', insurance))
    specialties = cursor.fetchall()
    zipcodes = [row[9] for row in specialties]
    find_closest = find_close(zipcodes, Zipcode, insurance, specialty)
    cursor.close()
    conn.close()
    return find_closest



def generate_doctor_recommendations(symptoms, age, gender, special_instructions):
    specialties = get_doctor_specialties()
    specialties_str = ", ".join(specialties)
    prompt = f"Patient (Age: {age}, Gender: {gender}) presents with the following symptoms: {symptoms}\n"
    prompt += f"Additional Information: {special_instructions}\n"
    prompt += f"Pick 3 relevant doctors specialties for the patient based on symptoms, age and additional information from these specialties: {specialties_str}\n"
    prompt += f"The specialties should come from the list I have provided above. Return Empty if no relevant specialties are found. Give the specialties name from the list word to word\n"
    prompt += f"Number the specialties too:\n"
    prompt += f"Keep in mind Pediatrics is for children and Geriatrics is for the elderly\n"
    
    # Generate the answer with OpenAI API using the prompt
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=50,  # Adjust max_tokens to limit the response length
        n=1  
    )
    # print(response)
    recommendations = [response.choices[0].message.content.split("\n")[2], response.choices[0].message.content.split("\n")[3], response.choices[0].message.content.split("\n")[4]]
    
    return recommendations

def initial(symptoms, age, gender, special_instructions):
    prompt = f"Patient (Age: {age}, Gender: {gender}) presents with the following symptoms: {symptoms}\n"
    prompt += f"Special Instructions: {special_instructions}\n"
    prompt += "Give an initial diagnosis based on the patient's symptoms and nothing else:\n"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=100,  # Adjust max_tokens to limit the response length
        n=3  
    )
    recommendations = [response.choices[0].message.content, response.choices[1].message.content, response.choices[2].message.content]
    # ''' response.choices[1]['message']['content'], response.choices[2]['message']['content']]'''
    return recommendations


@app.post("/find-doctors/")
async def find_doctors(symptom_model: SymptomModel):
    try:
        recommendations = generate_doctor_recommendations(
            symptom_model.symptoms,
            symptom_model.age,
            symptom_model.gender,
            symptom_model.special_instructions
        )
        # top_recommendations = recommendations[0].text.split("\n")[0].split(", ")
        return recommendations
    except:
        raise HTTPException(status_code=400, detail="Error Connecting to OpenAI API")

@app.post("/initial-diagnosis/")
async def initial_diagnosis(symptom_model: SymptomModel):
    try: 
        recommendations = initial(
            symptom_model.symptoms,
            symptom_model.age,
            symptom_model.gender,
            symptom_model.special_instructions
        )
        return recommendations
    except:
        raise HTTPException(status_code=400, detail="Error Connecting to OpenAI API")

    
@app.post("/get_doctors/")
async def get_doctors(insurance: Insurance):
    try:
        recommendations = get_doctor(
            insurance.specialty,
            insurance.insurance,
            insurance.Zipcode
        )
        return recommendations
    except:
        raise HTTPException(status_code=400, detail="Error Connecting to Snowflake")

class Zipcode(BaseModel):
    zipcode: str

@app.post("/hospital/")
async def hospital(zipcode: Zipcode):
    try:
        r = find_close_hospital(zipcode.zipcode)
        return r
    except:
        raise HTTPException(status_code=400, detail="Error Connecting to Snowflake")