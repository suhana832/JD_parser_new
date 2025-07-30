import streamlit as st
import os
import PyPDF2
import docx
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# Load API key from .env
load_dotenv()
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Use Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Extract text from various formats
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# Build structured prompt
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

# Convert AI response to downloadable PDF
def generate_pdf(content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph(line.strip(), styles["Normal"]) for line in content.split("\n") if line.strip()]
    elements.insert(0, Spacer(1, 12))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config("JD Parser AI", layout="wide")
st.title("📋 JD Parser – AI Assistant")
st.markdown("Upload a `.txt`, `.pdf`, or `.docx` Job Description and get structured AI-based output!")

uploaded_file = st.file_uploader("Upload JD File", type=["txt", "pdf", "docx"])

if uploaded_file:
    with st.spinner("📊 Processing the job description..."):
        jd_text = extract_text(uploaded_file)
        prompt = build_prompt(jd_text)

        try:
            response = model.generate_content(prompt)
            output = response.text

            st.success("✅ JD Parsed Successfully!")
            st.markdown("### 📄 Parsed JD Output:")
            st.markdown(output)

            pdf_buffer = generate_pdf(output)
            st.download_button("📥 Download Output as PDF", data=pdf_buffer, file_name="JD_Output.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"❌ Error: {e}")
