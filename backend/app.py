import os
import tempfile
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

app = Flask(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    return text[:12000]  # Limit to 12k characters

def generate_insights(text):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    As a policy analysis expert, provide concise insights from this document for decision-makers:
    1. Create 3-5 bullet points of key findings
    2. Highlight policy implications
    3. Identify potential risks/opportunities
    4. Suggest next actions
    ---DOCUMENT START---
    {text}
    ---DOCUMENT END---
    """
    
    payload = {
        "model": "deepseek-llm",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 512
    }
    
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File too large"}), 400
        file.seek(0)
        
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            file.save(tmp.name)
            text = extract_text_from_pdf(tmp.name)
            insights = generate_insights(text)
            
        return jsonify({
            "summary": insights,
            "key_points": insights.split("\n")[:5]
        })
    
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
