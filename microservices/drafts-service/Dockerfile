# Use a secure and slim base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy all code files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port if you're running a web server
EXPOSE 8002


# Start the app 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

