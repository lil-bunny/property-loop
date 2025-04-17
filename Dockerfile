FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with explicit versions of Google AI packages
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir google-generativeai==0.8.3 && \
    pip install --no-cache-dir google-ai-generativelanguage==0.6.10 && \
    pip install --no-cache-dir google-genai==1.2.0 && \
    pip list

# Install additional packages needed for python-magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the API server
# The PORT environment variable will be provided by Cloud Run
CMD ["python", "api_server.py"] 