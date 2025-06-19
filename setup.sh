#!/bin/bash

# Backend setup
echo "Setting up backend..."
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "Setup complete!"
echo "To start backend: source venv/bin/activate && python app.py"
echo "To start frontend: cd frontend && npm start"
