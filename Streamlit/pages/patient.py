import streamlit as st
import base64
import psycopg2
import time
import requests
import json
import pandas as pd
import bcrypt

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
set_bg_hack(st.secrets["IMAGE_PATH"])

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)


##############################################################################################################
#FASTAPI Functions
# Function to get Doctor Specialies:
def find_doctors(symptoms, age, gender, special_instructions):
    url = f"{st.secrets['FASTAPI_ENDPOINT']}/find-doctors/"
    data = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender,
        "special_instructions": special_instructions
    }
    response = requests.post(url, json=data)
    return response.json()

#function to get initial diagnosis
def initial_diagnosis(symptoms, age, gender, special_instructions):
    url = f"{st.secrets['FASTAPI_ENDPOINT']}/initial-diagnosis/"
    data = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender,
        "special_instructions": special_instructions
    }
    response = requests.post(url, json=data)
    return response.json()

#function to get doctors
def get_doctors(insurance, specialty, Zipcode):
    url = f"{st.secrets['FASTAPI_ENDPOINT']}/get_doctors/"
    data = {
        "insurance": insurance,
        "specialty": specialty,
        "Zipcode": Zipcode
    }
    response = requests.post(url, json=data)
    return response.json()

#function to get hospitals 
def get_hospitals(Zipcode):
    url = f"{st.secrets['FASTAPI_ENDPOINT']}/hospital/"
    data = {
        "zipcode": Zipcode
    }
    response = requests.post(url, json=data)
    return response.json()

# Function to check if session has timed out
def check_session_timeout(session_start_time, timeout_minutes=30):
    current_time = time.time()
    elapsed_time = current_time - session_start_time
    return elapsed_time > (timeout_minutes * 60)

##############################################################################################################
# App content
st.title('Patient Portal')
with st.expander("""### How to Navigate the Patient Portal"""):
            st.write("""

    #### Viewing Patient Details:
    - Once logged in, click on the 'Patient Details' expander to view your personal information.

    #### Using Key Features:

    **Enter Your Symptoms:**
    - Enter any symptoms you're experiencing in the 'Symptoms' text field.
    - Optionally, you can provide additional information in the 'Additional Information' field to give more context to your symptoms.

    **Finding Doctors and Hospitals:**
    - If you want to find doctors or hospitals near you, enter your Zipcode in the 'Zipcode' field.
    - Click on the respective buttons ('Doctors' or 'Hospitals') to get a list based on your input.

    **Initial Diagnosis:**
    - Click on 'Initial diagnosis' to receive a preliminary diagnosis based on the symptoms you've entered. This will be displayed under different hypotheses for your reference.

    **Exploring Doctor Recommendations:**
    - Under 'Personalized Doctors', you'll see a list of recommended doctors based on your symptoms and entered information.
    - Click on an expandable section for each doctor to see detailed information, including their practice, license status, and location.
    - Use the provided Google Maps link to find the doctor's location easily.

    **Finding Nearby Hospitals:**
    - When you click on 'Hospitals', the app will display a list of hospitals near the provided Zipcode.
    - The app shows hospital details and a link to their location on Google Maps for your convenience.
""")
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
        cursor.execute("SELECT * FROM patient WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            hashed_password = result[-1]
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            if hashed_password and check_password(hashed_password, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['session_start_time'] = time.time()
                st.session_state['patient_details'] = result 
            else:
                 st.warning("Incorrect Password")
        else:
            st.warning("Incorrect Username not found")

##############################################################################################################
# Session management and main app content
if st.session_state['logged_in']:
    # Check for session timeout
    if check_session_timeout(st.session_state['session_start_time']):
        st.session_state['logged_in'] = False
        st.warning("Session has timed out. Please login again.")
    else:
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

##############################################################################################################
        # INITIAL DIAGNOSIS
        if st.session_state['display_content'] == 'initial_diagnosis':
            if Symptoms != "":
                r = initial_diagnosis(Symptoms, age, gender, AI)
                st.subheader("Initial Diagnosis: According to the symptoms you have entered:")
                st.write("ranked with highest probability:")
                with st.expander("First Hypothesis"):
                    st.write(r[0])
                with st.expander("Second Hypothesis"):
                    st.write(r[1])
                with st.expander("Third Hypothesis"):
                    st.write(r[2])
            else:
                st.warning("Please enter Symptoms to get initial diagnosis.")
        
 ##############################################################################################################
        # DOCTORS       
        elif st.session_state['display_content'] == 'doctors':
            if Symptoms != "" and Zipcode != "" and Zipcode.isdigit() and len(Zipcode) == 5:
                r = find_doctors(Symptoms, age, gender, AI)
                # st.write(r)
                st.title("Personalized Doctors: ", )

                st.subheader(r[0])
                re = r[0].split(" ")
                remo = ' '.join(re[1:])
                results = get_doctors(insurance, remo, Zipcode)
                # print(results)
                if len(results)> 0: 
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
                            st.markdown(f'[Find the Doctor here](https://www.google.com/maps/search/?api=1&query={row[10]},{row[11]})', unsafe_allow_html=True)
                            st.markdown("[Book Appointment here](https://www.zocdoc.com/)")
                else:
                    st.subheader("No doctors found for these Symptoms in the current database.")
                    st.write("Please try again later. We keep Updating the database every week. Thank you for your patience.")
                    st.write("You can also try searching for doctors [here](https://www.zocdoc.com/).")
                st.subheader(r[1])
                re = r[1].split(" ")
                remo = ' '.join(re[1:])
                results = get_doctors(insurance, remo, Zipcode)
                if len(results)> 0:
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
                            st.markdown(f'[Find the Doctor here](https://www.google.com/maps/search/?api=1&query={row[10]},{row[11]})', unsafe_allow_html=True)
                            st.markdown("[Book Appointment here](https://www.zocdoc.com/)")
                else:
                    st.subheader("No doctors found for these Symptoms in the current database.")
                    st.write("Please try again later. We keep Updating the database every week. Thank you for your patience.")
                    st.write("You can also try searching for doctors [here](https://www.zocdoc.com/).")
                st.subheader(r[2])
                re = r[2].split(" ")
                remo = ' '.join(re[1:])
                results = get_doctors(insurance, remo, Zipcode)
                if len(results)> 0:
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
                            st.markdown(f'[Find the Doctor here](https://www.google.com/maps/search/?api=1&query={row[10]},{row[11]})', unsafe_allow_html=True)
                            st.markdown("[Book Appointment here](https://www.zocdoc.com/)")
                else:
                    st.subheader("No doctors found for these Symptoms in the current database.")
                    st.write("Please try again later. We keep Updating the database every week. Thank you for your patience.")
                    st.write("You can also try searching for doctors [here](https://www.zocdoc.com/).")
            else:
                st.warning("Please enter Symptoms and Zipcode (5 digits) to find personalized doctors.")

##############################################################################################################
        # HOSPITALS      
        elif st.session_state['display_content'] == 'hospitals':
            if Zipcode != "" and Zipcode.isdigit() and len(Zipcode) == 5:
                st.subheader("Hospitals near you: {}".format(Zipcode))
                results = get_hospitals(Zipcode)
                if len(results) == 0:
                    st.write("No hospitals found for this Zipcode. Please with another Zipcode.")
                    st.write("You can also try searching for hospitals [here](https://www.google.com/maps/search/hospitals+near+me/).")
                else:
                    df = pd.DataFrame(results)
                    df.columns = ['Hospital ID', 'Hospital Name', 'Zipcode', 'City', 'Latitude', 'Longitude', 'TimeZone']
                    df['Location'] = df.apply(lambda row: f'<a href="https://www.google.com/maps/search/?api=1&query={row.iloc[4]},{row.iloc[5]}" target="_blank">Maps</a>', axis=1)
                    df = df.drop(['Latitude', 'Longitude', 'TimeZone'], axis=1)
                    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.warning("Please enter a Zipcode (5 digits) to find hospitals near you.")
            
##############################################################################################################
        # Logout button
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

# Close the database connection
conn.close()

