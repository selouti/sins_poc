# sins_poc
Proof of concept for recast with modern architecture
# actors
customer 

service_agent

service_provider
# user stories
as a customer, i want to see if i am listed as a customer

as a service_agent, i want to see if the customer is listed

as a customer or service_agent, i want to have the option to search the customer list for one or more customers using incomplete customer information

as a service_agent, i want to create, update or delete customers in the customer list

as a service_agent, i want to record part or all of the following customer information: surname, name, dob, document number.

as a service_agent, i want to be able to add fields to the customer information list

as a service_provider, i want to maintain the list and provide it to service_agents

as a service_provider, i want to allow a customer to check for themselves or someone similiar in the list

as a service_provider, i want to authorise when the service_agent adds a field.

as a service_provider, i want to be able to remove a field

as a service_provider, i want to provide the list to service_agents at multiple distinct locations

as a service_provider, i want to ensure the list is syncronised between multiple distinct locations

as a service_provider, i want to ensure that a service agent can create, update or delete customers in the customer list

as a service_provider, i want to be able to delete customers from the list after a certain period of time

as a service_provider, i need to be able to report all transactions

# proposed architecture
https, python, kafka, ELK.

# environment
containers

---

# Quick start (MVP generated from this README)

This repository now includes a runnable Django application implementing the user stories below with:

- Django + Django REST Framework HTTP API
- Minimal web UI (index page with search form)
- Roles via simple request header `X-Role`: `customer`, `service_agent`, `service_provider`
- Customers CRUD, dynamic fields, exact and fuzzy search (configurable hit limit)
- Audit logging of transactions
- Kafka event publishing and consumers for multi-location synchronization (3 locations)
- Docker Compose stack with Kafka (Apache kafka-native, KRaft single-node; no ZooKeeper), Elasticsearch, and Kibana

## Run locally with Docker

Prerequisites: Docker and Docker Compose.

1) Build and start the stack (3 app instances + Kafka + Elasticsearch + Kibana):

```
docker compose up --build
```

2) Access the three locations:

- loc1: http://localhost:8001/
- loc2: http://localhost:8002/
- loc3: http://localhost:8003/

Kibana: http://localhost:5601/ (Elasticsearch at http://localhost:9200/)

Note: The stack uses the official Apache `apache/kafka-native` image running in KRaft (no ZooKeeper). If you ever need a clean broker state, stop the stack and prune the `kafkadata` volume:

```
docker compose down
docker volume rm sins_poc_kafkadata || true
docker compose up --build
```

3) API base (all locations):

- `GET/POST /api/customers/items/` — list/create customers (role: service_agent or service_provider to write)
- `GET/PUT/PATCH/DELETE /api/customers/items/{id}/` — retrieve/update/delete
- `GET /api/customers/items/search?q=...&mode=exact|fuzzy&limit=...` — search
- `GET/POST /api/customers/fields/` — list/add fields (role: service_provider)
- `PUT/PATCH/DELETE /api/customers/fields/{id}/` — update/remove fields (role: service_provider)

Set `X-Role` header to one of `customer`, `service_agent`, or `service_provider`.

4) Minimal UI

Open a location (e.g., loc1) in browser and use the search form. The UI sends the `X-Role` header.

### Sample data

The Compose services are configured to auto‑load sample data on first start. You can also load them manually:

```
# Load fixtures directly
python manage.py loaddata customers/fixtures/fields.json customers/fixtures/customers.json

# Or use the idempotent seeder (also used by Docker entrypoint when LOAD_SAMPLE_DATA=1)
python manage.py load_sample_data --extras 20
```

Troubleshooting auto‑load:

- The container entrypoint checks `LOAD_SAMPLE_DATA` (or `load_sample_data`) and accepts truthy values: `1`, `true`, `yes`, `on` (case‑insensitive).
- On startup it logs a line like `[entrypoint] LOAD_SAMPLE_DATA=1 → running python manage.py load_sample_data` in `app_loc{N}` logs.
- If you don't see this, set the variable in `docker-compose.yml` (already set for all three apps) or in your `.env`.
- You can also run seeding manually inside a container:

```
docker compose exec app_loc1 python manage.py load_sample_data --extras 10
```

Quick smoke test (from your host shell):

```
# List customers (read access with any role)
curl -s http://localhost:8001/api/customers/items/ -H 'X-Role: customer' | jq .

# Exact search (multiple terms are AND-ed across surname/name/document_number)
curl -s 'http://localhost:8001/api/customers/items/search?q=Alice%20Johnson&mode=exact' -H 'X-Role: customer' | jq .

# Fuzzy search (typo tolerant, limited by FUZZY_HIT_LIMIT)
curl -s 'http://localhost:8001/api/customers/items/search?q=Alyce%20Johnsen&mode=fuzzy' -H 'X-Role: customer' | jq .
```

To create/update/delete customers, use `X-Role: service_agent` (or `service_provider`).

5) Multi‑location sync

- Any create/update/delete in one location emits a Kafka event.
- Background consumers (one per location) apply events idempotently so the three locations stay in sync.

6) Data retention

- A simple worker runs `manage.py cleanup_customers` once a day to delete customers older than `RETENTION_DAYS` (default 365).

## Configuration

Environment variables (see defaults in `sins/settings.py`):

- `LOCATION_ID` — identifier for the running instance (loc1/loc2/loc3)
- `ROLE_HEADER` — request header carrying role (default `X-Role`)
- `FUZZY_HIT_LIMIT` — max results for fuzzy search (default 25)
- `RETENTION_DAYS` — retention period for customers (default 365)
- `KAFKA_BOOTSTRAP` — Kafka bootstrap (default `kafka:9092`)
- `ELASTICSEARCH_HOST` — Elasticsearch URL (default empty, not required)
- `DEBUG`, `SECRET_KEY` — standard Django settings

Sample‑data options:

- `LOAD_SAMPLE_DATA` — when set to `1`, the entrypoint runs `python manage.py load_sample_data` after migrations. This is enabled for the three app services in `docker-compose.yml`.
  - Accepted truthy values: `1`, `true`, `yes`, `on` (case‑insensitive). You may also use `load_sample_data` variable name.

You can also create a `.env` file at project root and set values; it will be read by the app.

## Development (without Docker)

1) Python 3.12 recommended. Create a virtualenv and install deps:

```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2) Initialize DB and runserver:

```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

3) Optional: run the Kafka consumer in another shell:

```
python manage.py consume_events
```

## Notes

- This PoC uses header-based roles for simplicity. Replace with real auth as needed.
- Fuzzy search uses RapidFuzz; tune `FUZZY_HIT_LIMIT` per service_provider.
- Logs are JSON-formatted to stdout; Elasticsearch/Kibana are provided to explore data, but log shipping is not wired via Logstash/Beats in this PoC.

### Admin

The Django admin is available at `/admin/`. Create a superuser in dev if needed:

```
python manage.py createsuperuser
```
