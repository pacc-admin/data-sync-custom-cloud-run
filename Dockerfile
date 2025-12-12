# Use Python 3.11 slim image (Based on Debian 12 Bookworm)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc-dev \
    unixodbc \
    odbcinst \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver for SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-cloud.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Không cần PORT nữa vì không phải Web Service

# Run the application using Python directly
# ENTRYPOINT cho phép nhận thêm tham số từ command line
ENTRYPOINT ["python", "main.py"]