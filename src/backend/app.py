import os
import tempfile
import requests
import logging
import sys
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF with error handling"""
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text[:12000]  # Limit to 12k characters
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        raise RuntimeError("Failed to extract text from PDF")

def generate_insights(text):
    """Generate insights using DeepSeek API with enhanced prompt"""
    if not text.strip():
        return "Document contained no extractable text"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enhanced policy-focused prompt
    prompt = f"""
    You are an expert policy analyst. Extract key insights from this document for senior government officials.
    Provide output in this EXACT format:
    
    ### EXECUTIVE SUMMARY
    [2-3 sentence overview of main content]
    
    ### KEY FINDINGS
    - Bullet point 1
    - Bullet point 2
    - Bullet point 3
    
    ### POLICY IMPLICATIONS
    - Impact on current policies
    - Recommended actions
    
    ### RISK ANALYSIS
    - Potential risks
    - Opportunities
    
    ---DOCUMENT START---
    {text}
    ---DOCUMENT END---
    """
    
    payload = {
        "model": "deepseek-llm",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL, 
            json=payload, 
            headers=headers,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API error: {str(e)}")
        return "Analysis failed: API service unavailable"
    except KeyError:
        logger.error("Unexpected API response format")
        return "Analysis failed: Could not process API response"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({"status": "healthy", "service": "pdf-insight-agent"})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and processing"""
    # Validate file presence
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Validate file type
    if not (file and allowed_file(file.filename)):
        return jsonify({"error": "Invalid file type. Only PDFs allowed"}), 400
    
    # Validate file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    
    if file_length > MAX_FILE_SIZE:
        return jsonify({
            "error": f"File too large. Max size: {MAX_FILE_SIZE//(1024*1024)}MB"
        }), 400
    
    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            logger.info(f"Processing file: {file.filename}")
            
            # Extract and process text
            text = extract_text_from_pdf(tmp_file.name)
            insights = generate_insights(text)
            
        # Clean up temporary file
        try:
            os.unlink(tmp_file.name)
        except OSError:
            pass
        
        # Format response
        return jsonify({
            "filename": secure_filename(file.filename),
            "summary": insights,
            "key_points": insights.split("\n")[:8]  # First 8 lines for preview
        })
    
    except Exception as e:
        logger.exception("Processing failed")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
