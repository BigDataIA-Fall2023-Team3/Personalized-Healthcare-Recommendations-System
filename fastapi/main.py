from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import snowflake.connector
import os

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

def get_doctor_specialties():
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT SPECIALITY FROM FP_DB.DATASETS_2.PRACTICE_SPECIALITIES;")
    specialties = [row[0] for row in cursor.fetchall()]
    # print(specialties)
    cursor.close()
    conn.close()
    return specialties

def get_doctor(specialty, insurance):
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()
    # Use placeholders for specialty and insurance variables
    cursor.execute("SELECT * FROM FP_DB.DATASETS_2.DOCTORS LEFT JOIN FP_DB.DATASETS_2.PRACTICE_SPECIALITIES ON DOCTORS.DOCTORS_ID = PRACTICE_SPECIALITIES.DOCTOR_ID WHERE speciality LIKE %s AND INSURANCE = %s;", (f'%{specialty}%', insurance))
    specialties = cursor.fetchall()
    cursor.close()
    conn.close()
    return specialties



def generate_doctor_recommendations(symptoms, age, gender, special_instructions):
    specialties = get_doctor_specialties()
    specialties_str = ", ".join(specialties)
    prompt = f"Patient (Age: {age}, Gender: {gender}) presents with the following symptoms: {symptoms}\n"
    prompt += f"Additional Information: {special_instructions}\n"
    prompt += f"Pick 3 relevant doctors specialties for the patient based on symptoms, age and additional information from these specialties: {specialties_str}\n"
    prompt += f"The specialties should come from the list I have provided above. Return Empty if no relevant specialties are found. Give the specialties name from the list word to word\n"
    prompt += f"Number the specialties too:\n"
    
    # Generate the answer with OpenAI API using the prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,  # Adjust max_tokens to limit the response length
        n=1  # Request up to 3 doctor recommendations
    )
    # print(response)
    recommendations = response.choices
    
    return recommendations

def initial(symptoms, age, gender, special_instructions):
    prompt = f"Patient (Age: {age}, Gender: {gender}) presents with the following symptoms: {symptoms}\n"
    prompt += f"Special Instructions: {special_instructions}\n"
    prompt += "Give an initial diagnosis based on the patient's symptoms and nothing else:\n"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,  
        n=3  
    )
    recommendations = [response.choices[0].text, response.choices[1].text, response.choices[2].text]
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
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while communicating with OpenAI")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while communicating with OpenAI")
    
@app.post("/get_doctors/")
async def get_doctors(specialty, insurance):
    try:
        recommendations = get_doctor(
            specialty,
            insurance
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while communicating with OpenAI")
