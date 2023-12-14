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

# Connect to the database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=5432  # Default PostgreSQL port
)
cursor = conn.cursor()
gender_choices = ["Male", "Female", "Other"]

fast_api_endpoint = "https://project-final-f9937888519e.herokuapp.com"

# Function to set background image
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
set_bg_hack('/Users/sumanayanakonda/Desktop/Final-Project/Streamlit/images/blue.jpeg')

# Function to get Doctor Specialies:


def find_doctors(symptoms, age, gender, special_instructions):
    url = 'https://project-final-f9937888519e.herokuapp.com/find-doctors/'
    data = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender,
        "special_instructions": special_instructions
    }
    response = requests.post(url, json=data)
    return response.json()

def initial_diagnosis(symptoms, age, gender, special_instructions):
    url = 'https://project-final-f9937888519e.herokuapp.com/initial-diagnosis/'
    data = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender,
        "special_instructions": special_instructions
    }
    response = requests.post(url, json=data)
    return response.json()

def get_doctors(insurance, specialty):
    url = 'https://project-final-f9937888519e.herokuapp.com/get_doctors/'
    data = {
        "insurance": insurance,
        "specialty": specialty
    }
    response = requests.post(url, json=data)
    return response.json()
  

def check_session_timeout(session_start_time, timeout_minutes=30):
    current_time = time.time()
    elapsed_time = current_time - session_start_time
    return elapsed_time > (timeout_minutes * 60)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'display_content' not in st.session_state:
    st.session_state['display_content'] = None

# Login functionality
if not st.session_state['logged_in']:
    st.sidebar.subheader("Login to Your Account")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        cursor.execute("SELECT * FROM patient WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['session_start_time'] = time.time()
            st.session_state['patient_details'] = result  # Store patient details
        else:
            st.warning("Incorrect Username/Password")

# Session management and main app content
if st.session_state['logged_in']:
    # Check for session timeout
    if check_session_timeout(st.session_state['session_start_time']):
        st.session_state['logged_in'] = False
        st.warning("Session has timed out. Please login again.")
    else:
        # Display user interface
        st.title(f"Welcome, {st.session_state['username']}!")

        # Show patient details
        patient_details = st.session_state['patient_details']
        patient_id, first_name, last_name, age, has_insurance, insurance, gender, username, password = patient_details
        with st.expander("Patient Details"):
            st.write(f"Patient ID: {patient_id}")
            st.write(f"First Name: {first_name}")
            st.write(f"Last Name: {last_name}")
            st.write(f"Age: {age}")
            st.write(f"Gender: {gender}")
            st.write(f"Does the Patient have Insurance?: {has_insurance}")
            if has_insurance:
                st.write(f"Insurance: {insurance}")
            st.write(f"Username: {username}")

        Zipcode = st.text_input("Zipcode (Optional)")
        Symptoms = st.text_input("Symptoms")
        AI = st.text_input("Optional: Additional Information")
        # Buttons for different information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Initial diagnosis", on_click=lambda: st.session_state.update({'display_content': 'initial_diagnosis'}))
        with col2:
            st.button("Doctors", on_click=lambda: st.session_state.update({'display_content': 'doctors'}))
        with col3:
            st.button("Hospitals", on_click=lambda: st.session_state.update({'display_content': 'hospitals'}))

        # Display content based on button click
        if st.session_state['display_content'] == 'initial_diagnosis':
            r = initial_diagnosis(Symptoms, age, gender, AI)
            st.subheader("Initial Diagnosis: According to the symptoms you have entered:")
            st.write("ranked with highest probability:")
            with st.expander("First Hypothesis"):
                st.write(r[0])
            with st.expander("Second Hypothesis"):
                st.write(r[1])
            with st.expander("Third Hypothesis"):
                st.write(r[2])
        
        
        elif st.session_state['display_content'] == 'doctors':
            r = find_doctors(Symptoms, age, gender, AI)
            st.title("Personalized Doctors: ", )
            st.subheader(r[0])
            re = r[0].split(" ")
            remo = ' '.join(re[1:])
            results = get_doctors(insurance, remo)
            for row in results:
                expander_title = f"{row[1]}"
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Doctor Name: {row[1]}")
                        st.write(f"Practice: {row[14]}")
                        st.write(f"License ID: {row[2]}")
                        st.write(f"License Status: {row[3]}")
                    with col2:
                        st.write(f"Accepts Medicaid: {row[4]}")
                        st.write(f"Accepts New Patients: {row[5]}")
                        st.write(f"Insurance: {row[6]}")
                        st.write(f"City: {row[7]}")
                        st.write(f"State: {row[8]}")
                        st.write(f"Zipcode: {row[9]}")
                    st.markdown("[Book Appointment here](https://www.zocdoc.com/)")

            st.subheader(r[1])
            re = r[1].split(" ")
            remo = ' '.join(re[1:])
            st.write(remo)
            results = get_doctors(insurance, remo)
            for row in results:
                expander_title = f"{row[1]}"
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Doctor Name: {row[1]}")
                        st.write(f"Practice: {row[14]}")
                        st.write(f"License ID: {row[2]}")
                        st.write(f"License Status: {row[3]}")
                    with col2:
                        st.write(f"Accepts Medicaid: {row[4]}")
                        st.write(f"Accepts New Patients: {row[5]}")
                        st.write(f"Insurance: {row[6]}")
                        st.write(f"City: {row[7]}")
                        st.write(f"State: {row[8]}")
                        st.write(f"Zipcode: {row[9]}")
                    st.markdown("[Book Appointment here](https://www.zocdoc.com/)")

            st.subheader(r[2])
            re = r[2].split(" ")
            remo = ' '.join(re[1:])
            st.write(remo)
            results = get_doctors(insurance, remo)
            for row in results:
                expander_title = f"{row[1]}"
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Doctor Name: {row[1]}")
                        st.write(f"Practice: {row[14]}")
                        st.write(f"License ID: {row[2]}")
                        st.write(f"License Status: {row[3]}")
                    with col2:
                        st.write(f"Accepts Medicaid: {row[4]}")
                        st.write(f"Accepts New Patients: {row[5]}")
                        st.write(f"Insurance: {row[6]}")
                        st.write(f"City: {row[7]}")
                        st.write(f"State: {row[8]}")
                        st.write(f"Zipcode: {row[9]}")
                    st.markdown("[Book Appointment here](https://www.zocdoc.com/)")
        
        elif st.session_state['display_content'] == 'hospitals':
            st.write("Hospital information goes here.")

        # Logout button
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

# Close the database connection
conn.close()



                
            
