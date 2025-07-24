from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import openai
import PyPDF2
from dotenv import load_dotenv

# Load OpenRouter API key
load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.endswith('.pdf'):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        file = request.files['jd_file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            jd_text = extract_text(file_path)

            prompt = f"""
You are an expert technical recruiter assistant.

Given the following job description (JD), generate output in **structured markdown** format with the following 3 sections:

---

### 1. ✅ Search Criteria

- **Boolean Keyword String** for sourcing candidates  
- **Mandatory Skills/Experience**  
- **Preferred Skills/Experience**  

---

### 2. 🧠 10 (ten) Screening Questions and Answers  
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
---
"""

            try:
                response = openai.ChatCompletion.create(
                    model="mistralai/mistral-7b-instruct:free",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=3500,  # increased token limit
                    timeout=180
                )
                result = response['choices'][0]['message']['content']
            except Exception as e:
                result = f"❌ Error: {e}"

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
