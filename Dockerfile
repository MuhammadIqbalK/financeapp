# syntax=docker/dockerfile:1

# ---- Stage 1: build the static SPA ----
FROM node:24-slim AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: backend + static frontend ----
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --frozen --no-install-project

COPY backend/alembic.ini backend/alembic ./
COPY backend/app ./app

COPY --from=frontend /build/build /frontend/build
ENV FRONTEND_DIR=/frontend/build

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
