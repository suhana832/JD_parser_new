import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from uploaded file
def extract_text(uploaded_file):
    if uploaded_file.name.endswith('.txt'):
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    return ""

# Streamlit UI
st.set_page_config(page_title="JD Parser AI", layout="centered")
st.title("📄 Job Description (JD) Parser using Gemini AI")

uploaded_file = st.file_uploader("Upload a JD file (.txt or .pdf)", type=["txt", "pdf"])

if uploaded_file:
    jd_text = extract_text(uploaded_file)

    st.markdown("### ✨ Preview Extracted JD Text")
    st.text_area("Extracted JD", jd_text, height=300)

    if st.button("🔍 Parse with AI"):
        with st.spinner("Generating AI Output..."):
            prompt = f"""
You are an expert technical recruiter assistant.

Given the following job description (JD), generate output in **structured markdown** format with the following 3 sections:

---

### 1. ✅ Search Criteria

- **Boolean Keyword String** for sourcing candidates  
- **Mandatory Skills/Experience**  
- **Preferred Skills/Experience**  

---

### 2. 🧠 10 Screening Questions and Answers  
Divide into categories below. Each question **must have an ideal answer**.
- **Domain Expertise**
- **Product/Tech Depth**
- **Cross-functional/Partner Management**
- **Fitment & Motivation**

---

### 3. 🗺️ Source Mapping
- Relevant companies in India (Chennai preferred)  
- Relevant job titles  
- LinkedIn search filters (Title, Skills, Location, Experience)

---

Job Description:
{jd_text}
"""

            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                st.success("✅ Parsed Successfully!")
                st.markdown("### 📋 AI Output")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"❌ Error: {e}")
