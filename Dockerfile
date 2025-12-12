# Use Python 3.11 slim image (Based on Debian 12 Bookworm)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Thêm gnupg2 và ca-certificates để xử lý key
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc-dev \
    unixodbc \
    odbcinst \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver for SQL Server (Updated for Debian 12 & non-deprecated key method)
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
ENV PORT=8080

# Run the application
# Lưu ý: Đảm bảo bạn đã có file main.py chạy app Flask/FastAPI
CMD exec gunicorn --bind :${PORT} --workers 1 --timeout 3600 main:app