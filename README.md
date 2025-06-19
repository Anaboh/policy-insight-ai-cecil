# Policy Insight Agent

AI-powered PDF analysis tool for policymakers

## Features
- PDF document summarization
- Key insights extraction
- Mobile-responsive design
- Policy-focused analysis

## Setup
1. Clone repo: `git clone https://github.com/yourusername/pdf-insight-agent`
2. Backend:
   
   cd backend
   pip install -r requirements.txt
   echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
   flask run
   

## Render.com Deployment
1. Create account at [render.com](https://render.com)
2. Create new Web Service -> Connect GitHub repo
3. Use `render.yaml` for configuration (pre-filled settings)
4. Set environment variables:
   - DEEPSEEK_API_KEY (your API key)
5. Deploy!

## Manual Deployment

# Initial setup
chmod +x setup.sh
./setup.sh

# Run backend
cd backend
source venv/bin/activate
flask run --port=5000

# Run frontend
cd ../frontend
npm start
