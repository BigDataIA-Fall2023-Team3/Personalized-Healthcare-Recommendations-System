import streamlit as st
import base64
import psycopg2
import pandas as pd
import bcrypt

def connect_db():
    return psycopg2.connect(
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        host=st.secrets["DB_HOST"],
        port=5432 
    )

def set_bg_hack(main_bg):
    main_bg_ext = "jpeg"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
         }}
         </style>
         """,
        unsafe_allow_html=True
    )
set_bg_hack(st.secrets["IMAGE_PATH"])

csv_file_path = st.secrets["INSURANCE_PATH"]
df = pd.read_csv(csv_file_path)
options = df.iloc[:, 0].unique().tolist()

def hash_password(password):
    pw =  bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return pw.decode('utf-8')


    

st.title('Welcome to the Personalized Healthcare Recommendation System')

with st.expander('Patient Guide', expanded=True):
    st.write('''
    ### Why use the Personalized Healthcare Recommendation System?
             
    #### Personalized Healthcare Guidance: 
    
    Patients receive tailored recommendations based on their symptoms, age, and other personal details, helping them identify potential health issues quickly.
    
    #### Easy Access to Healthcare Providers: 
    
    The app simplifies finding local doctors and hospitals, making it easier for patients to seek the care they need.
    #### Streamlined Registration and Insurance Information: 
    
    With a user-friendly sign-up process, patients can easily register and provide necessary information, including insurance details, enhancing their healthcare experience.
    Empowered Decision-Making: The app gives patients the tools and information to make informed decisions about their health, including the option to explore different healthcare providers and services.
    ''')

with st.expander("Patient Sign Up"):
    with st.form("Patient_Form"):
        patient_first_name = st.text_input("First Name")
        patient_last_name = st.text_input("Last Name")
        patient_age = st.number_input("Age", min_value=0, max_value=120)
        patient_has_insurance = st.radio("Do you have insurance?", ("Yes", "No"))
        patient_insurance = st.selectbox('Select an option:', options)
        patient_gender = st.selectbox('Select an Option:', ['Male', 'Female', 'Other'])
        patient_username = st.text_input("Username")
        patient_password = st.text_input("Password", type="password")
        
        submit_patient = st.form_submit_button("Sign Up as Patient")

        if submit_patient and patient_has_insurance == "Yes" and patient_insurance != "" and patient_first_name != '' and patient_last_name != '' and patient_age != '' and patient_gender != '' and patient_username != '' and patient_password != '':
            try:
                conn = connect_db()
                cursor = conn.cursor()
                hashed_password = hash_password(patient_password)
                cursor.execute("""INSERT INTO patient (first_name, last_name, age, has_insurance, insurance, gender, username, password) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", 
                            (patient_first_name, patient_last_name, patient_age, patient_has_insurance, patient_insurance, patient_gender, patient_username, hashed_password))
                conn.commit()
                st.success("Patient Registered Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
                conn.rollback()
            finally:
                if conn:
                    conn.close()
        else:
            st.warning("Please fill in all the fields")
            

with st.expander('Doctor Guide', expanded=True):
    st.write('''
### Why use the Personalized Healthcare Recommendation System?
#### Diagnostic Aid: 
The app serves as a diagnostic tool, helping doctors quickly assess patient symptoms, age, and gender to suggest possible diagnoses, enhancing clinical decision-making.
#### Treatment Planning: 
With access to a database of diseases and symptoms, doctors can explore various treatment options, tailor care plans to individual patient needs, and stay updated with the latest in healthcare protocols.
#### Efficiency in Patient Care: 
The app streamlines the process of patient assessment, allowing doctors to focus more on patient care and less on administrative tasks.
''')

with st.expander("Doctor Sign Up"):
    with st.form("Doctor_Form"):
        doctor_first_name = st.text_input("First Name")
        doctor_last_name = st.text_input("Last Name")
        doctor_practice = st.text_input("Practice")
        doctor_email = st.text_input("Email")
        doctor_username = st.text_input("Username", key="doctor_username")
        doctor_password = st.text_input("Password", type="password", key="doctor_password")
        submit_doctor = st.form_submit_button("Sign Up as Doctor")

        if submit_doctor and doctor_first_name != '' and doctor_last_name != '' and doctor_email != '' and doctor_username != '' and doctor_password != '':
            conn = connect_db()
            try:
                cursor = conn.cursor()
                hashed_password = hash_password(doctor_password)
                cursor.execute("""INSERT INTO doctor (first_name, last_name, practice, email, username, password) 
                                VALUES (%s, %s, %s, %s, %s, %s)""", 
                            (doctor_first_name, doctor_last_name, doctor_practice, doctor_email, doctor_username, hashed_password))
                conn.commit()
                st.success("Doctor Registered Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
        else:
            st.warning("Please fill in all the fields")
            
