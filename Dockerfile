# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_DIR=/app/workspace
ENV NOVA_HOME=/root/.nova

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY setup.py .
# Create a dummy src to satisfy setup.py if needed, or just install requirements
# using a generative approach to extract requirements would be better, but setup.py exists.
# We'll rely on pip installing from the current directory structure
COPY src/ src/
RUN pip install --no-cache-dir -e .

# Create workspace directory
RUN mkdir -p $WORKSPACE_DIR

# Copy the rest of the application
COPY . .

# Entrypoint
ENTRYPOINT ["nova"]
CMD ["start"]
