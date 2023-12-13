import streamlit as st

# Title
st.title("Patient Data Entry App")

# Input Fields
patient_name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=0, max_value=150, step=1)
gender = st.radio("Gender", ["Male", "Female", "Other"])
symptoms = st.text_area("Symptoms")
# diagnosis = st.text_area("Diagnosis")

# Address Section
st.subheader("Address")
street_address = st.text_input("Street Address")
city = st.text_input("City")
state_province = st.text_input("State/Province")
postal_code = st.text_input("Postal Code")
country = st.text_input("Country")


# Button to submit data
if st.button("Submit"):
    # You can process and store the data here (e.g., save it to a database)
    st.success("Data submitted successfully!")

# You can add further functionality for data processing and storage as needed.
