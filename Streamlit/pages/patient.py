import streamlit as st
import base64
import psycopg2
import time

# Database credentials
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
set_bg_hack('/Users/sumanayanakonda/Desktop/Final-Project/Streamlit/images/blue.jpeg')

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
        st.subheader("Patient Details")

        # Show patient details
        patient_details = st.session_state['patient_details']
        patient_id, first_name, last_name, age, gender, *other_details = patient_details
        st.write(f"Patient ID: {patient_id}")
        st.write(f"First Name: {first_name}")
        st.write(f"Last Name: {last_name}")
        st.write(f"Age: {age}")
        st.write(f"Gender: {gender}")
        # Add more patient details if needed

        # Buttons for different information
        st.button("Initial diagnosis", on_click=lambda: st.session_state.update({'display_content': 'initial_diagnosis'}))
        st.button("Doctors", on_click=lambda: st.session_state.update({'display_content': 'doctors'}))
        st.button("Hospitals", on_click=lambda: st.session_state.update({'display_content': 'hospitals'}))

        # Display content based on button click
        if st.session_state['display_content'] == 'initial_diagnosis':
            st.write("Initial diagnosis information goes here.")
        elif st.session_state['display_content'] == 'doctors':
            st.write("Doctor information goes here.")
        elif st.session_state['display_content'] == 'hospitals':
            st.write("Hospital information goes here.")

        # Logout button
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

# Close the database connection
conn.close()




                
            