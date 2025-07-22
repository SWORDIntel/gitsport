FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-async.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-async.txt

# Copy application files
COPY gitlab_async_tui_exporter.py .
COPY convert_config.py .

# Create necessary directories
RUN mkdir -p /app/exports

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ ! -f /app/gitlab_instances.txt ] && [ ! -f /app/config.json ]; then\n\
    echo "ERROR: No configuration found!"\n\
    echo "Mount either gitlab_instances.txt or config.json to /app/"\n\
    exit 1\n\
fi\n\
python gitlab_async_tui_exporter.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Volume for exports
VOLUME ["/app/exports"]

# Volume for config
VOLUME ["/app/gitlab_instances.txt"]

ENTRYPOINT ["/app/entrypoint.sh"]
