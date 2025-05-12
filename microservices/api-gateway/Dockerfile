# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Start FastAPI with hot reload in development (can change for prod)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
