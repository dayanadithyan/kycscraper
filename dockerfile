# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Set up a non-root user
RUN useradd -m appuser

# Set working directory
WORKDIR /app

# Copy only the necessary files
COPY --from=builder /root/.local /home/appuser/.local
RUN chown -R appuser:appuser /home/appuser/.local  # Add this line to fix permissions

COPY *.py entrypoint.sh ./

# Create output directory with proper permissions
RUN mkdir -p /app/output && \
    chown -R appuser:appuser /app

# Set PATH to include user installed packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV OUTPUT_DIR=/app/output
ENV PYTHONUNBUFFERED=1

# Set permissions
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os; exit(0 if os.path.exists('output') else 1)"]

# Run crawler when container starts
ENTRYPOINT ["./entrypoint.sh"]