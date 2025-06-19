#!/bin/bash

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
