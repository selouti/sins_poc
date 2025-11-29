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

### Adapted to `apache/kafka-native`

- Switched the Kafka service in `docker-compose.yml` to use the official Apache image `apache/kafka-native:3.7.0` (KRaft, no ZooKeeper).
- Replaced Bitnami-specific env vars with Apache-compatible settings:
  - `KAFKA_PROCESS_ROLES=broker,controller`, `KAFKA_NODE_ID=1`, `KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:9093`
  - `KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093`, `KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092`
  - `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT`, `KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER`
  - Added single-node-safe settings: `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1`, `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1`, `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1`, `KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS=0`
  - Set `KAFKA_CLUSTER_ID=mk00000000000000000000` and `KAFKA_LOG_DIRS=/var/lib/kafka/data`.
- Added a persistent volume for Kafka data: `kafkadata` → `/var/lib/kafka/data`.
- Updated README to document the switch to Apache kafka-native (KRaft) and how to reset the Kafka volume if needed.

### How to run
### How to run
1) Rebuild and start:
```
docker compose pull
docker compose up --build
```
2) Apps:
- loc1: http://localhost:8001/
- loc2: http://localhost:8002/
- loc3: http://localhost:8003/

If you need a clean Kafka state:
```
docker compose down
docker volume rm sins_poc_kafkadata || true
docker compose up --build
```

The application code and clients still use `KAFKA_BOOTSTRAP=kafka:9092` and require no code changes.

### What I changed
- Added simple browser-based CUD controls to `templates/index.html`:
  - "List customers" button
  - Create form (surname, name, dob, document_number, extra_fields JSON)
  - Update (PATCH) form by ID with optional fields
  - Delete form by ID
- Wired all forms to call the existing REST API using `fetch` and send the `X-Role` header from the Role input.

### How to use
- Open a location (e.g., http://localhost:8001/).
- In the "Role" field, set `service_agent` (or `service_provider` for field management).
- Use the new buttons/forms:
  - List → loads `/api/customers/items/`
  - Create → POSTs to `/api/customers/items/`
  - Update → PATCHes `/api/customers/items/{id}/`
  - Delete → DELETEs `/api/customers/items/{id}/`
- `extra_fields` must be valid JSON (e.g., `{ "notes": "VIP" }`).

### Notes
- Permissions are enforced via header-based roles, so CUD will only work when Role is `service_agent` or `service_provider`.
- If you want similar forms for managing dynamic fields (`/api/customers/fields/`), I can add a small section for that too.


- Extended `templates/index.html` with a new section for managing dynamic field definitions (`/api/customers/fields/`).
- Implemented buttons/forms wired to the existing API using `fetch`, sending the `X-Role` header from the Role input:
  - List fields → `GET /api/customers/fields/`
  - Create field → `POST /api/customers/fields/` (key, label, active)
  - Update field → `PATCH /api/customers/fields/{id}/` (optional: key, label, active; tri‑state checkbox to skip updating `active`)
  - Delete field → `DELETE /api/customers/fields/{id}/`
- Output reuses the existing JSON viewer panel.

#### How to use
1) Open a location (e.g., http://localhost:8001/).
2) Set Role to `service_provider`.
3) Use the new Dynamic fields section:
   - List → lists current field definitions.
   - Create → provide `key`, `label`, and whether it’s `active`.
   - Update → enter `id` and any fields you want to change; leave the active checkbox in its indeterminate (faded) state to skip changing `active`.
   - Delete → enter the `id`.

No backend changes were required; this UI talks to the existing endpoints and honors permissions.

### What I changed to make sample data auto‑loading reliable
- Hardened the Docker entrypoint logic so `LOAD_SAMPLE_DATA` is recognized in more cases and is clearly logged.
  - Accepts truthy values: `1`, `true`, `yes`, `on` (case‑insensitive) and also the lowercase var name `load_sample_data`.
  - Writes an explicit log line on startup indicating whether it will run the seeder.
- Added `LOAD_SAMPLE_DATA=1` to `.env.example` so it’s easy to enable while running locally.
- Documented troubleshooting in the README (how to verify via logs and how to trigger manual seeding).
- Added a safe fallback in `customers.apps.CustomersConfig.ready()` that will run `load_sample_data` once on Django startup when the env flag is set and the DB is ready but empty (useful outside Docker). It avoids interfering with `migrate`, `collectstatic`, tests, etc.

### Where to look for confirmation
- After `docker compose up --build`, check `app_loc1` logs for this line:
  - `[entrypoint] LOAD_SAMPLE_DATA=1 → running python manage.py load_sample_data`
- Then hit: `http://localhost:8001/api/customers/items/` (with header `X-Role: customer`) — you should see the seeded customers.
- Manual fallback: `docker compose exec app_loc1 python manage.py load_sample_data --extras 10`.

### Why it may not have loaded before
- The previous entrypoint only loaded when `LOAD_SAMPLE_DATA` was exactly `"1"`. Other common truthy values were ignored, and outside‑Docker runs had no auto‑load.
- Seeding is idempotent and only inserts when tables are empty; if a DB file (volume) already had data, it correctly skipped.

### Files changed
- `docker/entrypoint.sh`: tolerant flag parsing + startup logs
- `.env.example`: added LOAD_SAMPLE_DATA=1`
- `README.md`: troubleshooting and verification steps
- `customers/apps.py`: safe auto‑seed fallback when running with the env flag outside Docker

### Next steps for you
1) Pull the latest and rebuild: `docker compose up --build`
2) Watch `app_loc1` logs for the entrypoint line
3) Verify: `curl -s http://localhost:8001/api/customers/items/ -H 'X-Role: customer' | jq .`
4) If still empty, run manual: `docker compose exec app_loc1 python manage.py load_sample_data --extras 10`

If this still doesn’t populate, please share the first ~50 lines of `app_loc1` logs from startup so I can trace exactly what’s happening.

### Root cause
`loaddata` bypasses `auto_now_add`, so any field with `auto_now_add=True` and `null=False` must have a value provided in the fixture. Your model `customers.FieldDefinition.created_at` was `NOT NULL`, but the fixture entries didn’t include a `created_at` value, leading to:

```
django.db.utils.IntegrityError: ... NOT NULL constraint failed: customers_fielddefinition.created_at
```

### What I changed
- Made timestamp fields tolerant to fixtures that omit them:
  - `customers.models.FieldDefinition.created_at`: `DateTimeField(auto_now_add=True, null=True, blank=True)`
  - `customers.models.Customer.created_at`: `DateTimeField(auto_now_add=True, null=True, blank=True)`

These changes let fixtures load without providing `created_at`. Your app already runs `makemigrations` and `migrate` on startup (via `docker/entrypoint.sh`), so the schema will be updated automatically.
### What you need to do
- If running with Docker, simply rebuild/start to apply migrations and re-trigger seeding:
  - `docker compose up --build`
- If a previous, partially loaded DB exists and you want a clean start, remove the SQLite file or Docker volume before starting:
  - Docker volumes (Kafka reset shown already in README). For app DB you can just stop the stack and delete `db.sqlite3` in the project root if you don’t mind losing data.
- Verify in logs that sample data is loading (you should already see the entrypoint log for seeding when `LOAD_SAMPLE_DATA` is truthy). Then hit:
  - `http://localhost:8001/api/customers/items/` with header `X-Role: customer`.

### Notes
- Leaving `created_at` nullable is safe for a PoC and avoids brittle fixtures. If you prefer to keep NOT NULL, we can instead add explicit `created_at` values to the fixtures.
- `updated_at` continues to be maintained automatically on writes (`auto_now=True`).

If you still see errors after this, please share the first ~50 lines of `app_loc1` logs so I can trace any remaining issue.

### Fix applied: sample data fixtures now load without NOT NULL errors
Your `loaddata` run failed because `customers.Customer.updated_at` was `NOT NULL` and `auto_now=True` fields are not populated by `loaddata` (raw insert). I updated the model so fixtures can load cleanly:

- `customers.models.Customer.updated_at` → `DateTimeField(auto_now=True, null=True, blank=True)`
- `customers.models.Customer.created_at` and `customers.models.FieldDefinition.created_at` were already nullable as part of a previous change.

This removes the `NOT NULL constraint failed: customers_customer.updated_at` error when loading `customers/fixtures/customers.json`.

### What you need to do
- Rebuild/start the stack so the migration is generated and applied by the entrypoint:
  - `docker compose up --build`
- Confirm in logs you see:
  - Migrations run OK
  - `[entrypoint] LOAD_SAMPLE_DATA=1 → running python manage.py load_sample_data`
- Verify data:
  - `http://localhost:8001/api/customers/items/` with header `X-Role: customer` should list the seeded customers.

If you had a partially loaded DB and want a clean start, stop the stack and delete `db.sqlite3` (or prune the Docker volume if you mapped one), then start again.

If you prefer to keep `updated_at` NOT NULL in the future, we can also add explicit timestamps into the fixtures, but for the PoC, allowing NULL is simpler and robust for testing.

### Summary of the fix for `NoBrokersAvailable`

You saw your three Kafka consumer containers (`consumer_loc1/2/3`) exiting with `kafka.errors.NoBrokersAvailable`. I implemented resilience on both the infrastructure (Compose) and the app side so consumers only start once the broker is healthy and will keep retrying if it isn’t.

#### What changed
- Docker Compose
  - Added a healthcheck to the `kafka` service that runs `kafka-topics.sh --list` against `localhost:9092`.
  - Set `depends_on` with `condition: service_healthy` for `app_loc{1,2,3}` and `consumer_loc{1,2,3}` so they wait for Kafka to be healthy before starting.
  - Enabled topic auto-creation via `KAFKA_AUTO_CREATE_TOPICS_ENABLE=true` on the `apache/kafka-native` broker (convenient for the PoC).
  - Added `restart: unless-stopped` to all consumer services so they will keep retrying on transient failures.
- Consumers (`customers/management/commands/consume_events.py`)
  - Wrapped `KafkaConsumer` creation in a retry loop with exponential backoff and clear logging, so they don’t crash out on broker boot races; they keep retrying until Kafka is available.
- Producer (`sins/kafka_utils.py`)
  - Removed the previous behavior that could cache a failed producer init permanently. The producer now attempts to initialize on each emit if previously unavailable, allowing recovery when Kafka comes up later.

#### What you need to do
1) Rebuild and start (recommended to ensure the new healthcheck is in place):
```
docker compose up --build
```
2) If Kafka state is corrupted or from an older version, reset its volume then start:
```
docker compose down
# optional reset (will wipe broker data)
docker volume rm sins_poc_kafkadata || true
docker compose up --build
```
3) Watch logs:
- Kafka should report it’s up and the healthcheck will turn healthy.
- Consumers should log retries initially (if broker still starting), then print “Consumer started”.

4) Smoke test:
- Create/update/delete a customer via the UI or API on one location and confirm other locations reflect the change after a short delay.

If consumers still fail, please share the first 50–100 lines of logs from `kafka` and one of the `consumer_loc*` containers so I can diagnose further (advertised listeners or networking issues, etc.).

Fix ownership of the named volume to the UID used by the image (usually 1001):
# Inspect the volume name if unsure
docker volume ls | grep kafkadata

# (Optional) confirm image UID — if it prints 1001, use that below - returned 1000 on my machine
docker run --rm apache/kafka-native:4.1.1 id -u

# Chown the volume contents to that UID (1001 shown here)
docker run --rm -v sins_poc_kafkadata:/kdata alpine:3.19 \
  sh -c "chown -R 1000:1000 /kdata && ls -ld /kdata"


# See health status
docker compose ps

# Exec into the container and run the probe
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list; echo EXIT:$?
OCI runtime exec failed: exec failed: unable to start container process: exec: "/opt/kafka/bin/kafka-topics.sh": stat /opt/kafka/bin/kafka-topics.sh: no such file or directory
EXIT:127
docker compose exec sins_poc-kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list; echo EXIT:$?
service "sins_poc-kafka-1" is not running
EXIT:1

# Updated Kafka healthcheck applied
I updated docker-compose.yml to use the PATH-based probe you chose (Option A) and added a grace period so Kafka has time to warm up before Docker marks it unhealthy.
What changed in services.kafka.healthcheck:
• test: kafka-broker-api-versions.sh --bootstrap-server localhost:9092 (via PATH)
• interval: 10s, timeout: 10s, retries: 30
• start_period: 60s
# Next steps
1)
Recreate just Kafka and wait for health:
docker compose up -d --build kafka
docker compose ps
It may take a minute during the start_period before it turns healthy.
2)
If still unhealthy, run the probe inside the container and share output:
docker compose exec kafka sh -lc 'kafka-broker-api-versions.sh --bootstrap-server localhost:9092'; echo EXIT:$?
If the above command isn’t available in PATH on your image build, try the topics probe:
docker compose exec kafka sh -lc 'kafka-topics.sh --bootstrap-server localhost:9092 --list'; echo EXIT:$?
3)
After Kafka is healthy, your depends_on: condition: service_healthy will allow app_loc{1,2,3} and consumer_loc{1,2,3} to start. Verify consumers:
docker compose logs -f consumer_loc1 consumer_loc2 consumer_loc3
You should see them connect and print “Consumer started”.

# Notes
• Your previous log showed Kafka did start correctly; the issue was the healthcheck command/path and timing. The new probe via PATH plus start_period should resolve the “unhealthy” status.
• If you prefer, we can swap the probe to kafka-topics.sh --list via PATH instead; just tell me and I’ll adjust.
Let me know the result of docker compose ps after a minute or the exit code of the probe if it still shows unhealthy.

### What I changed
- Fixed Kafka startup/health issues in Docker Compose:
  - Replaced the failing script-based healthcheck with none because the `apache/kafka-native` image in your environment does not ship CLI scripts on PATH. Added a comment explaining this.
  - Relaxed `depends_on` from `condition: service_healthy` to simple service ordering for `app_loc{1..3}` and `consumer_loc{1..3}`. This leverages the existing retry logic I added earlier in the consumers and producer to handle broker warm-up.
- Previously addressed data-dir permission issue by recommending chown/bind mount; you confirmed Kafka now starts but healthcheck failed due to missing scripts. The new Compose settings align with that reality.

### What you need to do now
1) Recreate Kafka (and optionally whole stack):
```
docker compose up -d --build kafka
# or everything
docker compose up --build
```
2) Verify broker accessibility and consumer start:
```
docker compose logs -f consumer_loc1 consumer_loc2 consumer_loc3
```
You should see retries initially (if broker not ready yet), then “Consumer started”.
3) Smoke test cross-location sync by creating/updating/deleting a customer and observing replication.

### Optional (alternate healthcheck)
If you want a basic TCP healthcheck that doesn’t require Kafka CLI, we can add this later:
```
healthcheck:
  test: ["CMD-SHELL", "(</dev/tcp/localhost/9092) >/dev/null 2>&1 || exit 1"]
  interval: 5s
  timeout: 5s
  retries: 30
  start_period: 60s
```
This avoids CLI dependencies at the cost of being less semantic.

### Why this works
- Your broker log shows it started; the earlier unhealthy state was caused solely by a healthcheck command that didn’t exist in the image.
- Removing the brittle healthcheck plus leveraging robust retry logic ensures the stack comes up reliably across image/tag differences.
