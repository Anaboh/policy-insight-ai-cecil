FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# First copy only package.json to cache npm install
COPY frontend/package.json /app/frontend/
WORKDIR /app/frontend
RUN npm install

# Copy frontend source
COPY frontend /app/frontend

# Build frontend and verify
RUN npm run build && \
    mkdir -p /app/frontend_build && \
    mv build/* /app/frontend_build/ && \
    echo "Frontend build completed. Contents:" && \
    ls -la /app/frontend_build

# Set up backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend /app/backend

# Set working directory to backend
WORKDIR /app/backend

# Expose port and run server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
