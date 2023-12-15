import streamlit as st
import base64

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


# Check what content to display
st.title("About Our Healthcare Platform")

st.markdown("""
### Why Use Our Healthcare Platform?

**Personalized Healthcare at Your Fingertips:**

1. **Efficient Diagnosis and Doctor Search:**
- Our platform utilizes a unique algorithm to provide an initial diagnosis based on your symptoms. This helps in identifying potential health issues quickly and effectively.
- We offer a personalized doctor search feature. By inputting your symptoms, age, and gender, our system recommends doctors who specialize in treating your specific condition.

2. **Comprehensive Database Access:**
- Access a wide range of healthcare professionals and facilities. Whether you're looking for general practitioners, specialists, or hospitals, our database has updated and comprehensive listings.

3. **Convenient Location Services:**
- Find healthcare providers near you. Simply enter your Zipcode, and we'll show you the available hospitals and doctors in your area, complete with Google Maps links for easy navigation.

4. **Ease of Use:**
- Our user-friendly interface ensures that you can easily navigate through various services. Whether it's finding a doctor, looking up hospital locations, or getting an initial diagnosis, our platform is designed for ease and convenience.

5. **Secure and Private:**
- Your health information is sensitive. We prioritize your privacy and security, ensuring that your personal data is handled with the utmost confidentiality.

6. **Regular Updates:**
- We continuously update our database to include the latest information on doctors and healthcare facilities. This ensures you have access to current and relevant healthcare options.

7. **Streamlined Patient Experience:**
- From logging in to accessing your patient details and healthcare options, our platform streamlines your entire healthcare journey, saving you time and hassle.

**Empowering Your Health Decisions:**
Our platform is more than just a tool for finding healthcare services; it's a partner in your health journey. We empower you to make informed decisions about your health by providing relevant, up-to-date information and easy access to healthcare professionals.
""", unsafe_allow_html=True)


