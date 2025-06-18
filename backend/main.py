import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def extract_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(400, f"PDF processing error: {str(e)}")

def generate_insights(text):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    As a senior policy advisor, create a briefing from this document:
    {text[:15000]}
    
    Structure:
    1. 3-sentence executive summary
    2. Key impacts table (Sector | Severity | Affected Groups)
    3. Urgency rating (1-5 stars)
    4. Recommended next steps (3 bullet points)
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(500, "AI service error")
    
    return response.json()["choices"][0]["message"]["content"]

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files accepted")
    
    pdf_bytes = await file.read()
    text = extract_text(pdf_bytes)
    insights = generate_insights(text)
    
    return {"insights": insights}

@app.get("/")
def health_check():
    return {"status": "active", "service": "PolicyInsight AI"}
