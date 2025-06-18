import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PolicyInsight")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def health_check():
    return {"status": "active", "service": "PolicyInsight API"}

# Get API key from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logger.error("DeepSeek API key not set in environment variables")

def extract_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise HTTPException(400, f"PDF processing error: {str(e)}")

def generate_insights(text):
    if not DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key missing")
        raise HTTPException(500, "AI service not configured")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    As a senior policy advisor, create a briefing from this document:
    {text[:12000]}
    
    Structure your response with these sections:
    ## Executive Summary
    [3-sentence summary]
    
    ## Key Impacts
    [Table: Sector | Severity | Affected Groups]
    
    ## Urgency Assessment
    [Rating: 1-5 stars with justification]
    
    ## Recommended Actions
    [3 bullet points]
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions", 
            json=payload, 
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI API error: {str(e)}")
        raise HTTPException(500, f"AI service error: {str(e)}")

@app.post("/api/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files accepted")
    
    try:
        logger.info(f"Processing PDF: {file.filename}")
        pdf_bytes = await file.read()
        text = extract_text(pdf_bytes)
        logger.info(f"Extracted text: {len(text)} characters")
        
        insights = generate_insights(text)
        logger.info("Insights generated successfully")
        
        return {"insights": insights}
    except Exception as e:
        logger.exception("PDF analysis failed")
        raise HTTPException(500, f"Analysis failed: {str(e)}")
