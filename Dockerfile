# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create a non-root user for security
RUN useradd -m -u 1000 fireaprs && \
    chown -R fireaprs:fireaprs /app

# Switch to non-root user
USER fireaprs

# Default command (can be overridden)
CMD ["python", "main.py", "--help"]
