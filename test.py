import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models = genai.list_models()

print("\n✅ Available Gemini Models:\n")
for model in models:
    print(f"🔹 {model.name}")
