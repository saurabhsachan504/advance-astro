# Advance Astro

Privacy-first, self-hosted astrology application starter. It combines deterministic Vedic chart calculation with optional, consent-based visual-symbolic palm/face analysis. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the design and product boundaries.

## What this repository includes

- Next.js dashboard with birth-details form, chart facts, dual-insight workflow, and privacy controls.
- FastAPI backend with versioned routes, Pydantic validation, chart calculation, encrypted-field helpers, image lifecycle endpoints, and structured-report interface.
- PostgreSQL, Redis, Qdrant and an optional local model server via Docker Compose.
- Database initialization, local-only environment template, and a test suite for deterministic calculations.

## What you must provide before production

1. A `.env` created from `.env.example`, with strong unique secrets.
2. Swiss Ephemeris files in `data/ephemeris/` (or an explicitly documented package/data source).
3. A commercially licensed knowledge corpus for retrieval; do not ingest copyrighted texts without permission.
4. Validated palm/face models, an S3-compatible object-storage deployment, and a privacy/legal review. The supplied vision worker intentionally only performs image-quality and hand/face-presence checks; it does **not** claim to predict a future or recognise people.
5. Authentication provider, HTTPS reverse proxy, backups, monitoring, and a security review.

## Local start

```powershell
Copy-Item .env.example .env
# edit .env: replace every CHANGE_ME value
docker compose up --build
```

Open `http://localhost:3000` from the server. The web port is loopback-only; configure aaPanel/Caddy/Nginx as the public HTTPS reverse proxy. The API is intentionally private and is reached by the web app through its same-origin `/api` proxy; it is not published on a host port.

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

The system separates deterministic astronomical facts from optional interpretations. Do not market visual analysis as medical, scientific, identity, personality, financial, legal, or guaranteed-future assessment. Raw images are designed to be deletable immediately after analysis. Never expose PostgreSQL, Redis, Qdrant, object storage, or model-serving ports to the public internet.

## Optional: local visual analysis and feedback memory

The dashboard includes a consent-gated Palm/Face upload flow and a forecast-feedback workflow. Both are inactive until configured.

- Run a local OpenAI-compatible vision endpoint (for example, a Qwen-VL/LLaVA serving stack) on the private Docker network and set `VISION_LLM_BASE_URL` plus `VISION_LLM_MODEL` in `.env`.
- The API checks image quality, submits the image only to that configured local endpoint, and does not write the raw image to disk in this MVP. It never performs face recognition, identity matching, medical/demographic inference, or guaranteed predictions.
- Forecast feedback is stored as rule-level evidence (`yes`, `no`, or `unsure`); it does not retrain mathematical chart calculations or justify accuracy guarantees.
- To enable the optional Twilio WhatsApp dispatch worker, set all `TWILIO_*` values and `FEEDBACK_WORKER_SECRET`. Keep the dispatch endpoint private and invoke it from a trusted scheduler only.

## Multi-system engine

`POST /v1/charts/multi` calculates the same birth data through four transparent systems in one local request:

- Vedic / Parashari: sidereal Lahiri planets, ascendant, signs and nakshatras.
- KP: sidereal Placidus cusps and Vimshottari star-lord/sub-lord divisions.
- Numerology: life-path, birthday and attitude numbers.
- Western: tropical Placidus positions and major aspects.

The dashboard uses this route. These are calculations and interpretive frameworks, not evidence of guaranteed outcomes.

## Advanced deterministic tools

The local API also includes these no-LLM routes, and the web interface is available at `/advanced`:

- `POST /v1/dasha/vimshottari` — Vimshottari Mahadasha and Antardasha timeline.
- `POST /v1/kundli/interactive` — D1 whole-sign houses plus harmonic D9 and D10 data for North/South Indian UI layouts.
- `POST /v1/matchmaking/analyse` — transparent baseline Ashtakoota, Manglik flags, Moon star/sub-lord comparison, and tropical synastry aspects.
- `POST /v1/calendar/panchang` — Panchang facts, sunrise/sunset, Rahu Kaal, Choghadiya and next global eclipse events.
- `POST /v1/muhurat/plan` — baseline event-specific Choghadiya windows excluding Rahu Kaal, for a maximum 31-day range.

These calculations expose their rule assumptions. Local tradition, regional Panchang conventions, exceptions, and professional interpretation need additional rule packs before being used for consequential decisions.

## Extended advanced toolkit

The `Advanced` navbar control opens `/advanced/pro`, which additionally exposes:

- `POST /v1/gochar/live` for sidereal current transits, retrograde state, configured transit-to-natal aspects, and a Sade Sati phase indicator.
- `POST /v1/strengths/calculate` for deterministic Bhinna Ashtakavarga, Sarvashtakavarga house bindus, and transparent Uchcha/Kendra/Dig/motion/Naisargika strength components. Kala, Drik and tradition-specific Shadbala variants remain selectable-rule-pack work rather than hidden assumptions.
- `POST /v1/prashna/calculate` for question-time chart facts and Panchang context.
- `POST /v1/reports/chart.pdf` for a private, factual PDF of chart positions. It contains no AI interpretation.

## Private RAG knowledge base

RAG is included as a private Qdrant-backed retrieval layer. It requires a local OpenAI-compatible embedding server; it never needs a public AI API.

1. Set `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, and a strong `KNOWLEDGE_ADMIN_SECRET` in `.env`.
2. Ingest only text that you wrote, own, or are licensed to use with `POST /v1/knowledge/chunks` and header `X-Knowledge-Secret`.
3. Retrieve supporting passages with `POST /v1/knowledge/search`.

This starter deliberately returns sources and passages rather than claiming that a language model's output is an astrological fact. Connect a local LLM only after you have selected, evaluated and documented a model.

