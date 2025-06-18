FROM python:3.11-slim

# Install Node.js and build dependencies
RUN apt-get update && apt-get install -y curl build-essential
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

# Copy and build frontend
COPY frontend/package.json /app/frontend/
COPY frontend/package-lock.json /app/frontend/  # Add if exists
WORKDIR /app/frontend
RUN npm install

COPY frontend /app/frontend
RUN npm run build
RUN mv build /app/build

# Backend setup
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
