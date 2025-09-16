FROM python:3.10-slim

# Create app directory and storage link for backward compatibility
RUN mkdir -p /app/storage && ln -s /storage /app/storage

# Configure apt to handle potential proxy issues
RUN echo 'Acquire::http::Pipeline-Depth 0;\nAcquire::http::No-Cache true;\nAcquire::BrokenProxy true;\n' > /etc/apt/apt.conf.d/99fixbadproxy

# Install system dependencies
RUN apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update --fix-missing \
    && apt-get install -y \
        libglib2.0-0 \
        libglib2.0-dev \
        libgl1 \
        poppler-utils \
        libmagic1 \
        libmagic-dev \
        libpoppler-cpp-dev \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY pyproject.toml ./
COPY text_extract_api/__init__.py ./text_extract_api/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x /app/scripts/entrypoint.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]