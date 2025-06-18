import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import PyPDF2
from pathlib import Path
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

# Base directory - fixed path
BASE_DIR = Path("/app")
FRONTEND_BUILD = BASE_DIR / "frontend_build"
logger.info(f"Using fixed frontend path: {FRONTEND_BUILD}")

# Serve frontend build - only if exists
if FRONTEND_BUILD.exists() and FRONTEND_BUILD.is_dir():
    # FIXED: Corrected parentheses
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD), name="frontend")
    logger.info(f"Serving frontend from: {FRONTEND_BUILD}")
    
    @app.get("/favicon.ico")
    async def get_favicon():
        return FileResponse(FRONTEND_BUILD / "favicon.ico")
else:
    logger.error(f"Frontend build not found at: {FRONTEND_BUILD}")
    
    @app.get("/")
    async def fallback_frontend():
        return HTMLResponse("""
        <html>
            <head><title>PolicyInsight AI</title></head>
            <body>
                <h1>PolicyInsight AI</h1>
                <p>Frontend is building or missing. PDF API is available at /api/analyze</p>
                <p>Debug info: 
                    <br>Base dir: /app
                    <br>Frontend path: /app/frontend_build
                    <br>Exists: """ + str(FRONTEND_BUILD.exists()) + """
                </p>
            </body>
        </html>
        """)

# Health check
@app.get("/health")
def health_check():
    return {"status": "active", "service": "PolicyInsight AI"}

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
