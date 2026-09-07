# TOLTI AI

Local app / Modal cloud inference

## Install

```bash
# backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

## Scripts

```bash
# backend (run from backend/)
uvicorn app.main:app --reload --port 8000
pytest tests/
ruff check app tests

# frontend (run from frontend/)
npm run dev
npm run build
npm run preview
npm run typecheck
npm run lint
npm run format
npm run test
```

## Structure

```
backend/          FastAPI app, schemas, services, repositories
frontend/         React/TypeScript, esbuild bundle
infra/modal/      Modal deployment dependencies (separate from local app)
data/             Local SQLite DB and uploads (git-ignored)
docs/             PRD, architecture, contracts, decisions
scripts/          Project-level helper scripts
```

## Notes

- Frontend builds to a single self-contained `dist/index.html`.
- Modal deployment dependencies are isolated in `infra/modal/`.
- `.env.example` contains dummy names only. Copy to `.env` and fill real values locally.
- Backend health: `GET /api/v1/health/live` and `GET /api/v1/health/ready`.
