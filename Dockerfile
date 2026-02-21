# docker buildx build -t blk-hacking-ind-tejas-nakka .

# ============================================================
# Stage 1: Build React frontend
# ============================================================
FROM node:20-alpine AS frontend
# Alpine: minimal image size (~50MB), security-hardened, fast layer caching

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ============================================================
# Stage 2: Python API + serve built frontend
# ============================================================
FROM python:3.12-alpine
# Alpine Linux chosen for:
#   - Minimal footprint (~50MB base vs ~900MB for full Debian)
#   - Reduced attack surface (fewer packages = fewer CVEs)
#   - Fast container startup and pull times
#   - Suitable for stateless API workloads

WORKDIR /app

# Install build dependencies required by psutil (C extension)
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

# Install uv — significantly faster than pip (Rust-based resolver)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies first (layer caching optimization)
ENV UV_SYSTEM_PYTHON=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache

# Copy application source
COPY backend/ ./backend/

# Copy built frontend from stage 1
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Copy tests (for in-container test execution)
COPY test/ ./test/

ENV ENV=prod

EXPOSE 5477

# Run with uvicorn — single worker for hackathon simplicity
# Use --workers N for production multi-core utilization
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5477", "--workers", "3"]
