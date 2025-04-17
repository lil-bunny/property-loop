FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages needed for python-magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8002

# Command to run the API server
# Use 0.0.0.0 to listen on all interfaces and port 8002 (you can change port if needed)
CMD ["python", "api_server.py"] 