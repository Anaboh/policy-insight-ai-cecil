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
RUN npm install
RUN npm run build

# Move build to backend directory
RUN mkdir -p /app/backend/frontend_build
RUN mv build/* /app/backend/frontend_build/

# Set up backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend /app/backend

# Set final working directory
WORKDIR /app/backend

# Expose port and run server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
