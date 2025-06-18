import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import PyPDF2
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path configuration
current_dir = Path(__file__).parent
frontend_build = current_dir / "frontend_build"

# Check and serve frontend
if frontend_build.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build), html=True), name="frontend")
    print(f"✅ Frontend build found at {frontend_build}")
else:
    print(f"⚠️ Warning: Frontend build not found at {frontend_build}")
    
    @app.get("/")
    async def fallback_frontend():
        return HTMLResponse(content="<h1>PolicyInsight AI</h1><p>Frontend is building or missing. PDF API is available at /api/analyze</p>")

# Favicon endpoint
@app.get("/favicon.ico")
async def get_favicon():
    favicon_path = frontend_build / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return FileResponse("static/favicon.ico", status_code=404)

# Health check
@app.get("/health")
def health_check():
    return {"status": "active", "service": "PolicyInsight AI"}

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
    if not DEEPSEEK_API_KEY:
        raise HTTPException(500, "DeepSeek API key not configured")
    
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
    
    try:
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(500, f"AI service error: {str(e)}")

@app.post("/api/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files accepted")
    
    pdf_bytes = await file.read()
    text = extract_text(pdf_bytes)
    insights = generate_insights(text)
    
    return {"insights": insights}

@app.on_event("startup")
async def startup_event():
    print("Starting PolicyInsight AI server")
    print(f"Current directory: {current_dir}")
    print(f"Frontend build path: {frontend_build}")
    print(f"Build exists: {frontend_build.exists()}")
    if frontend_build.exists():
        print(f"Build contents: {list(frontend_build.glob('*'))}")
