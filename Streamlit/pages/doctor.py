import streamlit as st
import base64
import psycopg2
import time
import requests
import json
import pandas as pd

# Parameters for connecting to the database
db_host = st.secrets["DB_HOST"]
db_name = st.secrets["DB_NAME"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=5432  # Default PostgreSQL port
)
cursor = conn.cursor()
gender_choices = ["Male", "Female", "Other"]
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

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)


# Function to check if session has timed out
def check_session_timeout(session_start_time, timeout_minutes=30):
    current_time = time.time()
    elapsed_time = current_time - session_start_time
    return elapsed_time > (timeout_minutes * 60)
##############################################################################################################

#App Content
st.title('DOCTORS PORTAL')
with st.expander("""### How to Navigate the Doctor Portal"""):
            st.write("""
DOCUMENTATION
""")
            
##############################################################################################################
#Login          
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'display_content' not in st.session_state:
    st.session_state['display_content'] = None

if not st.session_state['logged_in']:
    st.sidebar.subheader("Login to Your Account")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        cursor.execute("SELECT * FROM doctor WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result and check_password(result[0].encode('utf-8'), password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['session_start_time'] = time.time()
            st.session_state['doctor_details'] = result  # Store patient details
        else:
            st.warning("Incorrect Username/Password")

##############################################################################################################
#Doctor Details
if st.session_state['logged_in']:
    # Check for session timeout
    if check_session_timeout(st.session_state['session_start_time']):
        st.session_state['logged_in'] = False
        st.warning("Session has timed out. Please login again.")
    else:
       # Show patient details
        doctor_details = st.session_state['doctor_details']
        doctor_id, doctor_f, doctor_l, doctor_p, doctor_e, doctor_username, doctor_password = doctor_details
        with st.expander("Doctor Details"):
            st.write(f"Doctor ID: {doctor_id}")
            st.write(f"First Name: {doctor_f}")
            st.write(f"Last Name: {doctor_l}")
            st.write(f"Practice: {doctor_p}")
            st.write(f"Email: {doctor_e}")
            st.write(f"Username: {doctor_username}")

        Gender = st.selectbox("Select the Gender of the Patient", gender_choices)
        Age = st.number_input("Enter the Age of the Patient", min_value=0, max_value=120)
        Symptoms = st.text_input("Symptoms")
        AI = st.text_input("Optional: Additional Information")

        if st.button("Submit"):
            st.session_state['display_content'] = 'Submit'

        if st.session_state['display_content'] == 'Submit':
            if Symptoms != '' and Age != '' and Gender != '':


                     # Insert THE DOCTOR CODE HERE.
                st.write("Submit")
            else:
                st.warning("Please fill in all the fields")
            
            # Insert THE DOCTOR CODE HERE.




##############################################################################################################
        
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

conn.close()

##############################################################################################################
def diagnose(symptoms):
   
    #  used  dummy diagnosis and treatment here
    diagnosis = "Common Cold"
    treatment = "Rest and stay hydrated"

    return diagnosis, treatment

def main():
    st.title("Medical Symptom Checker for Doctors")

    # Get patient symptoms from the user
    symptoms = st.text_area("Enter patient symptoms (comma-separated):")

    if st.button("Diagnose"):
        if symptoms:
            # Split the symptoms entered by the user
            symptom_list = [symptom.strip() for symptom in symptoms.split(',')]
            
            # Call the diagnose function
            diagnosis, treatment = diagnose(symptom_list)

            # Display the diagnosis and treatment
            st.success(f"Diagnosis: {diagnosis}")
            st.success(f"Treatment: {treatment}")
        else:
            st.warning("Please enter patient symptoms.")

