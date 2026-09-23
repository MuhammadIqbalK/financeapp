# Personal Finance App

A lightweight personal finance app for tracking daily income and expenses: dashboard, transactions, accounts, categories, budgets, transfers, and basic reports. Single-user MVP — see `prd.md` for the full specification.

## Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| Frontend | SvelteKit (TypeScript, static SPA)  |
| Backend  | FastAPI (Python)                    |
| Database | PostgreSQL                          |
| ORM      | SQLAlchemy + Alembic                |
| Auth     | JWT (PyJWT + bcrypt)                |
| Testing  | Pytest + Vitest + svelte-check      |

## Project layout

```text
├── prd.md               # Product requirements
├── Dockerfile           # Multi-stage: npm build + uvicorn
├── docker-compose.yml   # db + backend (serves API and SPA)
├── backend/
│   ├── app/
│   │   ├── main.py      # App + static SPA serving
│   │   ├── models.py    # SQLAlchemy models
│   │   ├── routers/     # auth, accounts, categories,
│   │   │                # transactions, transfers, budgets,
│   │   │                # dashboard, reports
│   │   └── config.py    # Settings (reads backend/.env)
│   ├── alembic/         # DB migrations
│   ├── tests/           # Pytest suite
│   ├── .env.example     # Copy to backend/.env
│   └── .env             # Secrets (never commit)
└── frontend/
    └── src/
        ├── lib/api/     # API clients
        ├── lib/components/
        └── routes/      # login, dashboard, transactions,
                         # accounts, categories, budgets, settings
```

## Prerequisites

- Python 3.14 + [uv](https://docs.astral.sh/uv/)
- Node.js 24 + npm
- PostgreSQL 16+ (any reachable instance)

## Environment

Secrets live only in `.env` files — both are git-ignored.

```bash
# Backend (required)
cp backend/.env.example backend/.env
# edit backend/.env: DATABASE_URL, SECRET_KEY

# Docker Compose only (required before `docker compose up`)
cp .env.example .env
# set POSTGRES_PASSWORD
```

| Variable                   | Where          | Purpose                                   |
| -------------------------- | -------------- | ----------------------------------------- |
| `DATABASE_URL`             | `backend/.env` | Postgres connection string                |
| `SECRET_KEY`               | `backend/.env` | JWT signing key (required, no default)    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `backend/.env` | Token lifetime (optional, default 30 days) |
| `CORS_ORIGINS`             | `backend/.env` | Allowed origins (optional)                |
| `FRONTEND_DIR`             | optional       | Static SPA directory (default `frontend/build`) |
| `POSTGRES_PASSWORD`        | root `.env`    | Compose DB password (required for compose) |
| `POSTGRES_USER` / `POSTGRES_DB` / `POSTGRES_PORT` / `APP_PORT` | root `.env` | Compose overrides (optional) |

## Run locally (development)

```bash
# 1. Database — any Postgres; create the database first:
#    createdb financeapp   (or via psql)

# 2. Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev            # http://localhost:5173 → proxies to API on :8000
```

API: <http://localhost:8000/api/health> · OpenAPI docs: <http://localhost:8000/docs>

Register an account at `/login` to get started — default income/expense categories are seeded automatically.

## Run with Docker Compose

```bash
cp .env.example .env            # then set POSTGRES_PASSWORD
docker compose up --build
```

- App (API + SPA): <http://localhost:8000>
- Postgres exposed on host port `5441` (override with `POSTGRES_PORT` if needed)
- App secrets are read from `backend/.env`; nothing secret is in `docker-compose.yml`

## Production-style single server (static SPA)

```bash
cd frontend && npm run build     # outputs frontend/build/
cd ../backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Uvicorn serves the built SPA and falls back to `index.html` for client-side routes; `/api/*` and `/docs` are handled by FastAPI first. Same-origin calls mean no CORS configuration is needed.

## Tests & checks

```bash
# Backend
cd backend
uv run ruff check app tests      # lint
uv run pytest                    # 6 tests

# Frontend
cd frontend
npm run check                    # svelte-check (0 errors)
npm test                         # vitest
npm run build                    # production build
```

## API overview

| Area         | Endpoints                                                                  |
| ------------ | -------------------------------------------------------------------------- |
| Auth         | `POST /api/auth/register`, `POST /api/auth/login`, `GET/PUT /api/auth/me`  |
| Accounts     | `GET/POST /api/accounts`, `GET/PUT/DELETE /api/accounts/{id}`              |
| Categories   | `GET/POST /api/categories`, `PUT/DELETE /api/categories/{id}`              |
| Transactions | `GET/POST /api/transactions`, `GET/PUT/DELETE /api/transactions/{id}`      |
| Transfers    | `GET/POST /api/transfers`, `PUT/DELETE /api/transfers/{id}`                |
| Budgets      | `GET/POST /api/budgets`, `PUT/DELETE /api/budgets/{id}`                    |
| Dashboard    | `GET /api/dashboard?period=today\|week\|month\|custom`                     |
| Reports      | `GET /api/reports/summary`, `/api/reports/expense-breakdown`, `/trend`    |

All endpoints except register/login require `Authorization: Bearer <token>`.

## Financial rules

- **Account balance** = initial balance + income − expense + transfer in − transfer out
- **Total balance** = sum of all account balances
- **Savings** = income − expenses (selected period)
- **Budget** = remaining (`budget − category expenses`) and usage % (`spent / budget × 100`)
