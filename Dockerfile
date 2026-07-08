# MatchDay Command Center — Multi-stage Docker Build
# Stage 1: Build frontend (Node)
# Stage 2: Run backend + serve static assets (Python slim)

# ---- Stage 1: Frontend build ----
FROM node:20-alpine AS frontend
WORKDIR /frontend

# Copy dependency manifests first for layer caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Runtime ----
FROM python:3.12-slim AS runtime

# Disable .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency manifest first for layer caching
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/app ./app

# Copy built frontend from stage 1
COPY --from=frontend /frontend/dist ./static

# Create non-root user (UID 10001)
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
