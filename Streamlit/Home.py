import streamlit as st
import base64
import psycopg2
import pandas as pd

def connect_db():
    return psycopg2.connect(
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        host=st.secrets["DB_HOST"],
        port=5432  # Default PostgreSQL port
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
set_bg_hack('/mount/src/final-project/Streamlit/images/blue.jpeg')

csv_file_path = /mount/src/final-project/Streamlit/Insurance.csv'
df = pd.read_csv(csv_file_path)
options = df.iloc[:, 0].unique().tolist()

def add_patient(username, password, first_name, last_name, age, has_insurance, insurance, gender):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Modify the query based on your table structure
        cursor.execute("INSERT INTO patient (first_name, last_name, age, has_insurance, insurance, gender, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                       (first_name, last_name, age, has_insurance, insurance, gender, username, password))
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def add_doctor(username, password, other_details):
    conn = connect_db()
    cursor = conn.cursor()
    # Modify the query based on your table structure
    cursor.execute("INSERT INTO doctor (username, password, other_details) VALUES (%s, %s, %s)", 
                   (username, password, other_details))
    conn.commit()
    conn.close()

st.title('Welcome to the Personalized Healthcare Recommendation System')

with st.expander('Patient Guide'):
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

        if submit_patient:
            add_patient(patient_username, patient_password, patient_first_name, patient_last_name, patient_age, patient_has_insurance, patient_insurance, patient_gender)  # Add appropriate function arguments
            st.success("Patient Registered Successfully!")

with st.expander('Doctor Guide'):
    st.write('''
    1. Click on the 'Sign Up' button if you havent registered already.
    2. Enter your credentials and click on 'Login' in the doctor page.
    3. View your patients and their recommendations.
    ''')

with st.expander("Doctor Sign Up"):
    with st.form("Doctor_Form"):
        doctor_username = st.text_input("Username", key="doctor_username")
        doctor_password = st.text_input("Password", type="password", key="doctor_password")
        # Add other necessary fields
        submit_doctor = st.form_submit_button("Sign Up as Doctor")

        if submit_doctor:
            add_doctor(doctor_username, doctor_password, "other details here")  # Add appropriate function arguments
            st.success("Doctor Registered Successfully!")
