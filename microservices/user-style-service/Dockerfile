# Use full Python image to speed up install of heavy packages like numpy, sklearn
FROM python:3.10

# Set environment variable for NLTK data
ENV NLTK_DATA=/usr/share/nltk_data

# Set working directory
WORKDIR /app

# Pre-copy requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies (keep cache for faster rebuilds in dev)
RUN pip install -r requirements.txt

# Clean NLTK data directory and download required resources
RUN rm -rf /usr/share/nltk_data/* && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt averaged_perceptron_tagger

# Now copy the rest of the code
COPY . .

# Expose port and set entrypoint
CMD ["sh", "wait-for-db.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
