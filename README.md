# Backend

This folder contains the FastAPI service that owns the portfolio's SQLite database, admin auth, sessions, and contact submissions.

## Run locally

From the repo root:

```bash
uv run --project backend uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Environment variables

- `PORTFOLIO_BACKEND_API_URL`
  Example: `https://backend-f5c9d745.fastapicloud.dev`
- `PORTFOLIO_BACKEND_DB_PATH`
  Optional custom SQLite path. Defaults to `tmp/portfolio.sqlite`
- `PORTFOLIO_ADMIN_EMAIL`
  Optional bootstrap admin email
- `PORTFOLIO_ADMIN_PASSWORD`
  Optional bootstrap admin password
- `PORTFOLIO_SESSION_SECRET`
  Shared secret used to sign admin session tokens across replicas

If `PORTFOLIO_ADMIN_EMAIL` and `PORTFOLIO_ADMIN_PASSWORD` are set, the backend will create that admin user automatically when the database starts.

## SQLite note

SQLite works well for a single backend instance. If your platform runs multiple replicas, each replica can end up with its own local SQLite file. Stateless signed sessions avoid cross-replica login failures, but contact submissions still need a single shared database or a single backend replica for fully consistent reads and writes.
