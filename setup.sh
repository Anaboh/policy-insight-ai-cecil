#!/bin/bash

# Backend setup
echo "Setting up backend..."
cd src/backend
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ../..

# Frontend setup
echo "Setting up frontend..."
cd src/frontend
npm install
cd ../..

echo "Setup complete!"
echo "To start backend: cd src/backend && source venv/bin/activate && python app.py"
echo "To start frontend: cd src/frontend && npm start"
