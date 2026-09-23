# Backend

FastAPI + SQLAlchemy + Alembic. See the [project README](../README.md) for full setup, environment variables, and Docker instructions.

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# checks
uv run ruff check app tests
uv run pytest
```

Configuration is read from `backend/.env` (copy `.env.example`).
