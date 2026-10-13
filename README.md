# AeroPulse backend

Django REST Framework backend for the AeroPulse maintenance-planning MVP. It keeps the API, persistence and future Python ML integration in one codebase.

## Start locally

```bash
uv sync --group dev
uv run python manage.py migrate
uv run python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/api/`. Create an admin user with
`uv run python manage.py createsuperuser` only if you need Django admin access.

## Authentication status

All API endpoints are intentionally public during development. Bruno requests do
not need a bearer token. JWT and token code remains in the project for a later
authentication phase; re-enable protected routes before any deployment with
real or sensitive data.

## Current endpoints

- `GET /api/fleet/overview` — fleet readiness summary.
- `GET /api/fleet/aircraft/{aircraft_id}` — internal aircraft profile.
- `GET /api/fleet/aircraft/{aircraft_id}/telemetry` — latest component telemetry.
- `GET /api/fleet/aircraft/{aircraft_id}/risk` — latest component risk scores.
- `POST /api/fleet/imports/telemetry` — upload and process telemetry CSV data.
- `GET /api/fleet/maintenance/queue` — proposed maintenance work orders.
- `POST /api/fleet/work-orders` — create a pending work order.
- `GET /api/fleet/inventory` and `GET /api/fleet/inventory/forecast` — spare-part inventory.
- `GET /api/fleet/iaf/fleet` — latest imported GlobalMilitary IAF fleet snapshot.
- `GET, POST /api/fleet/squadrons/` — IAF squadrons.
- `GET, PUT, PATCH, DELETE /api/fleet/squadrons/{squadron_id}/` — one squadron.
- `GET, POST /api/fleet/squadron-aircraft/` — individual aircraft assigned to squadrons.
- `GET /api/fleet/squadron-aircraft/?squadron={squadron_id}` — an individual squadron's aircraft.
- `GET, POST /api/maintenance/tasks/` — maintenance tasks.

`fleet/services.py` is the integration boundary for feature engineering and model inference. Replace the TODO with a worker-backed ML pipeline later; the HTTP contract does not need to change.

## Supabase PostgreSQL

1. Create a Supabase project and copy its PostgreSQL connection URI from **Connect**.
2. Copy `.env.example` to `.env`, then put that URI in `DATABASE_URL`. The backend loads `.env` automatically. URL-encode special characters in the database password.
3. Run `uv run python manage.py migrate` to create the schema in Supabase.

The backend uses SQLite if `DATABASE_URL` is absent, so local work stays simple. Supabase is selected automatically when the variable is present. Do not use Supabase's anon key or service-role key as a database password.

## Verification

```bash
uv run pytest
uv run python manage.py check
```

## Fabricated demo data

Generate a deterministic, non-sensitive six-month dataset with:

```bash
uv run python scripts/generate_fabricated_data.py
```

It writes CSVs to `data/fabricated/`, including 30 aircraft, six subsystem inventories, 32,400 daily telemetry records, training labels, fault events and resolved maintenance work orders. `AF-117` has a deliberately visible hydraulic-pump degradation window followed by repair.

## Public IAF fleet snapshot

The command below fetches the public HTML inventory table from GlobalMilitary.net, normalizes the Indian Air Force rows, and keeps the source URL plus retrieval timestamp with that snapshot. This is a manual import command, not an API integration; use it sparingly and comply with the source's applicable terms.

```bash
uv run python manage.py scrape_iaf_fleet
```

Read the latest stored import at `GET /api/fleet/iaf/fleet`. The returned payload attributes the source and does not claim the third-party data is first-party or real-time.

## Public IAF squadron import

This command imports named **Flying Units** labelled Squadron or Sqn from the
public Bharat-Rakshak IAF units index. It intentionally excludes flights,
missile, radar, and signal units. The source does not provide a base or
aircraft count on the index, so those fields are left blank.

```bash
uv run python manage.py scrape_iaf_squadrons
```

Use `--dry-run` to inspect the parsed record count without writing to the
database.

## Squadron aircraft records

`SquadronAircraft` represents an individually identifiable aircraft assigned
to a squadron. Each record stores a unique aircraft number, aircraft name,
country of origin, year inducted, flight hours, maintenance dates, and role.
The public squadron index does not provide this aircraft-level information, so
create these records through the API or Bruno after importing the squadron list.

Example request:

```http
POST /api/fleet/squadron-aircraft/
Content-Type: application/json

{
  "squadron": "YOUR_SQUADRON_ID",
  "aircraft_number": "SB-001",
  "aircraft_name": "Su-30MKI",
  "country_of_origin": "India / Russia",
  "year_inducted": 2002,
  "flight_hours": "1842.5",
  "last_maintenance_on": "2026-09-30",
  "next_maintenance_on": "2026-12-30",
  "operational_role": "Air superiority"
}
```
