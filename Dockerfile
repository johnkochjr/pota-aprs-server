FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir aprslib requests

# Copy server script
COPY pota_server.py .

# Create logs directory
RUN mkdir -p /app/logs

# Run with unbuffered output for better logging
CMD ["python", "-u", "pota_server.py"]
