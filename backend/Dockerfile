# ==========================================
# Stage 1: Build stage
# ==========================================
FROM python:3.12-slim AS builder
WORKDIR /app

# Set environment variables
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

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install runtime dependencies (e.g., libpq for postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder stage and install them
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application source code
COPY . .

# Copy project files
COPY . .

# Build arg for API URL — baked into the build at compile time
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build Vite application
RUN npm run build

# Create a non-root system user and adjust permissions
RUN addgroup --system django && \
    adduser --system --ingroup django django-user && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django-user:django /app

# Expose production port
EXPOSE 8000

# Switch to the non-root user
USER django-user

# Run Gunicorn
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]