import streamlit as st

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

if __name__ == "__main__":
    main()
