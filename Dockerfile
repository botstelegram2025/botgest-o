# Dockerfile simplificado para Railway
FROM python:3.11-slim

# Install Node.js and system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Install Node.js dependencies for Baileys
WORKDIR /app/baileys-server
RUN npm install

# Back to main directory
WORKDIR /app

# Create auth directory
RUN mkdir -p /app/baileys-server/auth_info

# Set environment variables
ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT=production

# Expose ports
EXPOSE 5001
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Start command
CMD ["python3", "start_railway.py"]