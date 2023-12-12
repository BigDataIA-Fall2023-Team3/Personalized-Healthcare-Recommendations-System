import streamlit as st
import psycopg2
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

# Function to connect to the RDS PostgreSQL database
def connect_to_database():
    return psycopg2.connect(
        host='bigdata.cvyew2wvbapg.us-east-2.rds.amazonaws.com',
        user='Team3',
        password='Bigdata3',
        dbname='postgres',
        port='5432'
    )

# Streamlit App Code
st.title('User Registration and Login')

menu = ['Home', 'Login', 'SignUp']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'SignUp':
    st.subheader("Create New Account")
    new_first_name = st.text_input("First Name")
    new_last_name = st.text_input("Last Name")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type='password')

    if st.button("SignUp"):
        if not new_first_name or not new_last_name or not new_email or not new_password:
            st.warning("Please fill out all fields.")
        elif not is_valid_email(new_email):
            st.error("Invalid email format.")
        elif not is_valid_password(new_password):
            st.error("Password must be at least 8 characters long and include 1 alphabet, 1 number, and 1 special character.")
        else:
            conn = connect_to_database()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", (new_email,))
            if cur.fetchone():
                st.warning("An account with this email already exists.")
            else:
                hashed_password = hash_password(new_password)
                cur.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                            (new_first_name, new_last_name, new_email, hashed_password))
                conn.commit()
                st.success("You have successfully created an account")
            conn.close()


elif choice == 'Login':
    st.subheader("Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if email and password:
            if not is_valid_email(email):
                st.error("Invalid email format")
            else:
                hashed_password = hash_password(password)
                conn = connect_to_database()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
                data = cur.fetchone()
                conn.close()
                if data:
                    st.success("Logged In as {}".format(data[1]))
                else:
                    st.warning("Incorrect Email/Password")
        else:
            st.warning("Please fill out all fields.")
