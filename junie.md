## What I built
- A runnable Django MVP generated from your README, including:
  - Django + DRF API and a minimal web UI (index page with a search form)
  - Header-based roles using `X-Role` for `customer`, `service_agent`, and `service_provider`
  - Customers CRUD, dynamic field management, exact and fuzzy search (RapidFuzz) with a configurable hit limit
  - Append-only audit logs for transactions
  - Kafka producer for mutations and a consumer management command for multi-location sync (idempotent)
  - JSON logging suitable for ELK
  - Dockerfile and docker-compose with 3 app instances (loc1/loc2/loc3), Kafka (KRaft), Elasticsearch, Kibana, consumers, and a retention worker

### Key files/folders
- `manage.py`, `sins/settings.py`, `sins/urls.py`, `sins/wsgi.py`, `sins/asgi.py`, `sins/simpleauth.py`, `sins/kafka_utils.py`
- `customers/` app: `models.py`, `serializers.py`, `views.py`, `permissions.py`, `urls.py`, `admin.py`
- `audit/` app: `models.py`, `admin.py`
- Management commands:
  - `customers/management/commands/consume_events.py` (Kafka consumer)
  - `customers/management/commands/cleanup_customers.py` (retention)
- Minimal UI: `templates/index.html`
- Containerization: `docker/Dockerfile`, `docker/entrypoint.sh`, `docker-compose.yml`
- Config and deps: `.env.example`, `requirements.txt`
- Updated `README.md` with setup, usage, and role instructions

### How to run (quick)
1) `docker compose up --build`
2) Open: loc1 http://localhost:8001, loc2 http://localhost:8002, loc3 http://localhost:8003
3) Try the search form; set header Role in the page input (defaults to `customer`).
4) API paths (all locations):
   - `GET/POST /api/customers/items/`
   - `GET/PUT/PATCH/DELETE /api/customers/items/{id}/`
   - `GET /api/customers/items/search?q=...&mode=exact|fuzzy&limit=...`
   - `GET/POST /api/customers/fields/`, `PUT/PATCH/DELETE /api/customers/fields/{id}/` (service_provider)

### Notes
- By design for the PoC: simple header-based roles, SQLite DB, Kafka+ELK via compose. Easily swappable to production services later.
- Fuzzy search uses RapidFuzz and respects `FUZZY_HIT_LIMIT` (configurable via env).
- Multi-location sync is event-driven; each location has a consumer with idempotent apply.
- Retention worker runs daily to delete customers older than `RETENTION_DAYS`.

### Added sample data fixtures and seeding flow
- Created Django fixtures:
  - `customers/fixtures/fields.json` with example dynamic fields (`middle_name`, `alt_phone`, `notes`).
  - `customers/fixtures/customers.json` with 10 diverse customers (names, typos/variants for fuzzy, accents, punctuation).
- Added idempotent management command `load_sample_data`:
  - Loads fixtures if tables are empty and optionally generates extra demo customers via `--extras N`.
  - Safe to run multiple times.
- Wired optional auto‑load on container start:
  - `docker/entrypoint.sh` runs `python manage.py load_sample_data` when `LOAD_SAMPLE_DATA=1`.
  - Enabled `LOAD_SAMPLE_DATA=1` for `app_loc1`, `app_loc2`, `app_loc3` in `docker-compose.yml`.
- Updated README with a "Sample data" section:
  - Manual commands using `loaddata` or `load_sample_data --extras 20`.
  - Curl smoke tests for exact and fuzzy search.
  - Mentioned `LOAD_SAMPLE_DATA` flag and admin usage.

### How to use
- Docker: `docker compose up --build` (sample data loads automatically on first start).
- Manual: `python manage.py loaddata customers/fixtures/fields.json customers/fixtures/customers.json` or `python manage.py load_sample_data --extras 20`.
- Verify: `curl -s http://localhost:8001/api/customers/items/ -H 'X-Role: customer'` or try fuzzy search via `/api/customers/items/search?...&mode=fuzzy`.