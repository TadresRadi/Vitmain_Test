# ==========================================
# Stage 1: Build stage
# ==========================================
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies and build wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ==========================================
# Stage 2: Final run stage
# ==========================================
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder stage and install them
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application source code (includes templates, management commands, etc.)
COPY . .

# Create a non-root system user and adjust permissions
RUN addgroup --system django && \
    adduser --system --ingroup django django-user && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django-user:django /app

# Copy entrypoint script (as root, before switching to django-user)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose production port
EXPOSE 8000

# Switch to the non-root user
USER django-user

# Entrypoint runs migrations + seed_db, then exec's the CMD (gunicorn)
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]