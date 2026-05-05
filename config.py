from __future__ import annotations

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
TMP_DIR = PROJECT_ROOT / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = Path(
    os.environ.get("PORTFOLIO_BACKEND_DB_PATH", TMP_DIR / "portfolio.sqlite")
).resolve()

ADMIN_EMAIL = os.environ.get("PORTFOLIO_ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.environ.get("PORTFOLIO_ADMIN_PASSWORD", "").strip()

