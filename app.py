import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# PDF/TXT Text Extractor
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    else:
        return file.read().decode("utf-8")

# Prompt Template
def build_prompt(jd_text):
    return f"""
You are an expert technical recruiter assistant.

Given the following job description (JD), generate output in structured markdown format with the following 3 sections:

---

### 1. ✅ Search Criteria
- Boolean Keyword String  
- Mandatory Skills/Experience  
- Preferred Skills/Experience  

---

### 2. 🧠 10 Screening Questions and Answers  
Categorize into:
- Domain Expertise  
- Product/Tech Depth  
- Cross-functional/Partner Management  
- Fitment & Motivation  
(Provide ideal answers too)

---

### 3. 🗺️ Source Mapping
- Companies in India (Chennai preferred)  
- Relevant job titles  
- LinkedIn Filters (Title, Skills, Location, Experience)

---

JD:
{jd_text}
"""

# UI
st.set_page_config("JD Parser AI", layout="wide")
st.title("📋 JD Parser – AI Assistant")
st.markdown("Upload a `.txt` or `.pdf` Job Description and get structured insights!")

uploaded_file = st.file_uploader("Upload Job Description File", type=["txt", "pdf"])

if uploaded_file:
    with st.spinner("Extracting and analyzing JD..."):
        jd_text = extract_text(uploaded_file)
        prompt = build_prompt(jd_text)

        try:
            response = model.generate_content(prompt)
            st.success("✅ Parsed Successfully!")
            st.download_button("📥 Download Output", response.text, file_name="JD_Output.md")
            st.markdown("### 📄 Parsed JD Output:")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ Error: {e}")
