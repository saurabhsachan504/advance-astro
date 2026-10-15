# Advance Astro

Privacy-first, self-hosted astrology application starter. It combines deterministic Vedic chart calculation with optional, consent-based visual-symbolic palm/face analysis. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the design and product boundaries.

## What this repository includes

- Next.js dashboard with birth-details form, chart facts, dual-insight workflow, and privacy controls.
- FastAPI backend with versioned routes, Pydantic validation, chart calculation, encrypted-field helpers, image lifecycle endpoints, and structured-report interface.
- PostgreSQL, Redis, Qdrant, MinIO and optional vLLM services via Docker Compose.
- Database initialization, local-only environment template, and a test suite for deterministic calculations.

## What you must provide before production

1. A `.env` created from `.env.example`, with strong unique secrets.
2. Swiss Ephemeris files in `data/ephemeris/` (or an explicitly documented package/data source).
3. A commercially licensed knowledge corpus for retrieval; do not ingest copyrighted texts without permission.
4. Validated palm/face models and a privacy/legal review. The supplied vision worker intentionally only performs image-quality and hand/face-presence checks; it does **not** claim to predict a future or recognise people.
5. Authentication provider, HTTPS reverse proxy, backups, monitoring, and a security review.

## Local start

```powershell
Copy-Item .env.example .env
# edit .env: replace every CHANGE_ME value
docker compose up --build
```

Open `http://localhost:3000`. API docs are at `http://localhost:8001/docs`.

For frontend-only iteration:

```powershell
cd apps/web
npm install
npm run dev
```

For backend tests:

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Safety and privacy

The system separates deterministic astronomical facts from optional interpretations. Do not market visual analysis as medical, scientific, identity, personality, financial, legal, or guaranteed-future assessment. Raw images are designed to be deletable immediately after analysis. Never expose PostgreSQL, Redis, Qdrant, MinIO, or model-serving ports to the public internet.

