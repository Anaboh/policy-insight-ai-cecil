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
import os

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

# Enhanced debug info at startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting PolicyInsight AI server")
    
    # Base directory - fixed path
    base_dir = Path("/app")
    logger.info(f"Base directory: {base_dir}")
    
    # List root directory contents
    try:
        root_contents = os.listdir("/")
        logger.info(f"Root directory contents: {root_contents}")
    except Exception as e:
        logger.error(f"Error listing root directory: {str(e)}")
    
    # Check application directory
    try:
        app_contents = os.listdir("/app")
        logger.info(f"/app directory contents: {app_contents}")
    except Exception as e:
        logger.error(f"Error listing /app directory: {str(e)}")
    
    # Verify frontend build location
    frontend_build_path = base_dir / "frontend_build"
    logger.info(f"Frontend build path: {frontend_build_path}")
    
    if frontend_build_path.exists():
        logger.info(f"Frontend build found! Contents: {os.listdir(frontend_build_path)}")
        static_files = StaticFiles(directory=str(frontend_build_path))
        app.mount("/", static_files, name="frontend")
        logger.info("Frontend mounted successfully")
    else:
        logger.error(f"Frontend build not found at: {frontend_build_path}")

# Serve frontend if exists
@app.get("/")
async def serve_frontend_or_fallback():
    frontend_path = Path("/app/frontend_build/index.html")
    
    if frontend_path.exists():
        return FileResponse(frontend_path)
    
    return HTMLResponse(f"""
    <html>
        <head><title>PolicyInsight AI</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>PolicyInsight AI</h1>
            <p>Frontend is building or missing. PDF API is available at /api/analyze</p>
            
            <h3>Debug Information</h3>
            <pre>
Base directory: /app
Frontend path: /app/frontend_build
Exists: {frontend_path.exists()}

Directory contents:
{os.listdir('/app') if Path('/app').exists() else 'Directory /app not found'}
            </pre>
        </body>
    </html>
    """)

# Favicon endpoint
@app.get("/favicon.ico")
async def get_favicon():
    favicon_path = Path("/app/frontend_build/favicon.ico")
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return JSONResponse({"error": "Favicon not found"}, status_code=404)

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
