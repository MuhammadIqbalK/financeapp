from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .routers import (
    accounts,
    auth,
    budgets,
    categories,
    dashboard,
    reports,
    transactions,
    transfers,
)

settings = get_settings()

app = FastAPI(title="Personal Finance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth.router,
    accounts.router,
    categories.router,
    transactions.router,
    transfers.router,
    budgets.router,
    dashboard.router,
    reports.router,
):
    app.include_router(router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Static SPA (frontend/build) — registered after the API routes so /api/* wins.
# ---------------------------------------------------------------------------
_frontend_dir = Path(settings.frontend_dir).resolve()


def _serve_spa(full_path: str) -> FileResponse:
    if full_path:
        candidate = (_frontend_dir / full_path).resolve()
        if candidate.is_relative_to(_frontend_dir) and candidate.is_file():
            return FileResponse(candidate)
    index = _frontend_dir / "index.html"
    if index.is_file():
        return FileResponse(index, media_type="text/html")
    from fastapi import HTTPException

    raise HTTPException(
        status_code=404, detail="Frontend not built. Run `npm run build` in frontend/."
    )


if _frontend_dir.is_dir():

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        return _serve_spa(full_path)

    @app.head("/{full_path:path}", include_in_schema=False)
    def spa_head(full_path: str):
        return _serve_spa(full_path)
