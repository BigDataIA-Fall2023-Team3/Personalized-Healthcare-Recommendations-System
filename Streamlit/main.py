import streamlit as st
import psycopg2
import psycopg2.extras
import hashlib
import re

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate email using regex
def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None

# Function to validate password using regex
def is_valid_password(password):
    return re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", password) is not None

# Function to validate license ID (example validation, can be adjusted)
def is_valid_license_id(license_id):
    return re.match(r"^\d{5,6}$", license_id) is not None

# Function to connect to the RDS PostgreSQL database
def connect_to_database():
    return psycopg2.connect(
        host='bigdata.cvyew2wvbapg.us-east-2.rds.amazonaws.com',
        user='Team3',
        password='Bigdata3',
        dbname='postgres',
        port='5432'
    )

# Function to check if the email exists in the database
def user_email_exists(email):
    with connect_to_database() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            return cur.fetchone() is not None

# Function to check if the email exists in the doctors table
def doctor_email_exists(email):
    with connect_to_database() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM doctors WHERE email=%s", (email,))
            return cur.fetchone() is not None

def doctor_license_exists(license_id):
    with connect_to_database() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM doctors WHERE license_id=%s", (license_id,))
            return cur.fetchone() is not None

# Function to insert a new user into the database
def insert_new_user(first_name, last_name, email, hashed_password):
    with connect_to_database() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, hashed_password)
            )
            conn.commit()

def insert_new_doctor(first_name, last_name, license_id, email, hashed_password):
    with connect_to_database() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO doctors (first_name, last_name, license_id, email, password) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, license_id, email, hashed_password)
            )
            conn.commit()       


def authenticate_user(email, hashed_password, table_name):
    with connect_to_database() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            query = f"SELECT * FROM {table_name} WHERE email=%s AND password=%s"
            cur.execute(query, (email, hashed_password))
            return cur.fetchone()

# Streamlit App Code
st.title('User Registration and Login')

menu = ['Home', 'Login', 'SignUp']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'SignUp':
    st.subheader("Register As")
    role = st.radio("Choose your role:", ('Patient', 'Doctor'))

    if role == 'Patient':
        with st.form("Patient Signup Form"):
            new_first_name = st.text_input("First Name")
            new_last_name = st.text_input("Last Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type='password')
            submit_button = st.form_submit_button("SignUp as Patient")

            if submit_button:
                if not (new_first_name and new_last_name and new_email and new_password):
                    st.warning("Please fill out all fields.")
                elif not is_valid_email(new_email):
                    st.warning("Invalid email format.")
                elif not is_valid_password(new_password):
                    st.warning("Password must be at least 8 characters long and include 1 alphabet, 1 number, and 1 special character.")
                elif user_email_exists(new_email):
                    st.warning("An account with this email already exists.")
                else:
                    hashed_password = hash_password(new_password)
                    insert_new_user(new_first_name, new_last_name, new_email, hashed_password)
                    st.success("You have successfully created a Patient account")

    elif role == 'Doctor':
        with st.form("Doctor Signup Form"):
            new_first_name = st.text_input("First Name")
            new_last_name = st.text_input("Last Name")
            new_license_id = st.text_input("License ID")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type='password')
            submit_button = st.form_submit_button("SignUp as Doctor")

            if submit_button:
                if not (new_first_name and new_last_name and new_license_id and new_email and new_password):
                    st.warning("Please fill out all fields.")
                elif not is_valid_email(new_email):
                    st.warning("Invalid email format.")
                elif not is_valid_license_id(new_license_id):
                    st.warning("License ID must contain only numbers between 5-6 digits.")
                elif not is_valid_password(new_password):
                    st.warning("Password must be at least 8 characters long and include 1 alphabet, 1 number, and 1 special character.")
                elif doctor_license_exists(new_license_id):
                    st.warning("License ID already exists.")    
                elif doctor_email_exists(new_email):
                    st.warning("An account with this email already exists.")
                else:
                    hashed_password = hash_password(new_password)
                    insert_new_doctor(new_first_name, new_last_name, new_license_id, new_email, hashed_password)
                    st.success("You have successfully created a Doctor account")

if choice == 'Login':
    st.subheader("Login to Your Account")

    # Callback to reset fields
    def reset_login_form():
        st.session_state['email'] = ''
        st.session_state['password'] = ''

    # Role selection with callback to reset fields
    role = st.radio("Login as:", ('Patient', 'Doctor'), on_change=reset_login_form)

    with st.form("User Login Form"):
        email = st.text_input("Email", key='email')
        password = st.text_input("Password", type='password', key='password')
        login_button = st.form_submit_button("Login")

    if login_button:
        if not (email and password):
            st.warning("Please fill out all fields.")
        elif not is_valid_email(email):
            st.error("Invalid email format.")
        else:
            hashed_password = hash_password(password)
            table_name = 'doctors' if role == 'Doctor' else 'users'
            user_data = authenticate_user(email, hashed_password, table_name)
            if user_data:
                st.success(f"Logged In as {user_data['first_name']}")
            else:
                st.warning("Incorrect Email/Password")