# Use a Python 3.10 base image with devcontainer support
FROM mcr.microsoft.com/devcontainers/python:3.10

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    # PostgreSQL headers for psycopg2 / databases
    libpq-dev \
    # Python headers for building wheels
    python3-dev \
    gnupg \
    ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (correct source setup)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools (important for modern wheels)
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /workspaces/autoagent

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Optional: set shell for VS Code terminal convenience
SHELL ["/bin/bash", "-c"]
