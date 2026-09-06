# ==============================================================================
# DecisionSphere — Production Multi-Stage Dockerfile
# Service: FastAPI REST Backend & Multi-Domain Simulation Engine
# Security: Unprivileged execution under non-root appuser (UID 10001)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build & Dependency Wheel Compilation
# ------------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS builder

# Prevent Python from writing .pyc files and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install build-time dependencies for native C/C++ extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment for runtime export
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy canonical dependency specification
COPY requirements.txt .

# Filter out Windows-only platform dependencies (e.g. pywinpty) during Linux container build
# Host requirements.txt remains 100% untouched
RUN grep -v "pywinpty" requirements.txt > /tmp/requirements-linux.txt && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements-linux.txt

# ------------------------------------------------------------------------------
# Stage 2: Minimal Secure Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runtime

LABEL maintainer="DecisionSphere Engineering Team" \
      description="DecisionSphere Strategic Planning & Risk Evaluation Platform Backend" \
      version="1.0.0"

# Install minimal shared C libraries required by PostgreSQL, XGBoost, and health probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create deterministic non-root system user and group (Security requirement)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m -d /home/appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Configure environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV="production"

WORKDIR /app

# Ensure /app directory is owned by appuser
RUN chown appuser:appgroup /app

# Copy root configuration and migration descriptor
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup docker-entrypoint.sh .

# Copy application layers, authoritative model artifacts, and benchmark data cohorts
COPY --chown=appuser:appgroup src/ src/
COPY --chown=appuser:appgroup backend/ backend/
COPY --chown=appuser:appgroup models/ models/
COPY --chown=appuser:appgroup data/ data/

# Ensure entrypoint is executable
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Healthcheck configuration using standard /api/v1/health probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

# Deterministic entrypoint: Postgres readiness -> alembic migrations -> uvicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
