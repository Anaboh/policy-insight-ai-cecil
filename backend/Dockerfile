FROM python:3.11-slim

# Install Node.js and build dependencies
RUN apt-get update && apt-get install -y curl build-essential
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

# Copy backend requirements first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files
COPY frontend /app/frontend

# Build frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Move build to backend directory
RUN mv build /app/backend/frontend_build

# Copy backend source code
WORKDIR /app
COPY backend /app/backend

# Create static directory for fallback favicon
RUN mkdir -p /app/backend/static
COPY frontend/public/favicon.ico /app/backend/static/

EXPOSE 8000
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
