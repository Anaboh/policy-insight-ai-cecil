FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy frontend files
COPY frontend /app/frontend

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Create frontend build directory
RUN mkdir -p /app/frontend_build && \
    mv build/* /app/frontend_build/ && \
    echo "Frontend build contents:" && \
    ls -la /app/frontend_build

# Set up backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend /app/backend

# Verify final structure
RUN echo "Final /app contents:" && \
    ls -la /app && \
    echo "Frontend build contents:" && \
    ls -la /app/frontend_build

# Set working directory to backend
WORKDIR /app/backend

# Expose port and run server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
