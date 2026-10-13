# AeroPulse backend

Django REST Framework backend for the AeroPulse maintenance-planning MVP. It keeps the API, persistence and future Python ML integration in one codebase.

## Start locally

```bash
uv sync --group dev
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/api/`. Sign in through `/admin/` while developing, or add token/JWT authentication before deploying.

Create a bearer token for Bruno after migrations:

```bash
uv run python manage.py drf_create_token YOUR_USERNAME
```

Copy the generated token into the selected Bruno environment's `token` variable.

## JWT authentication

Use cookie-based JWT authentication for the Next.js frontend. Access tokens last 15 minutes. Refresh tokens last 7 days and rotate whenever they are refreshed. Both cookies are HttpOnly, so browser JavaScript cannot read the refresh token.

| Method | Endpoint | Request body |
| --- | --- | --- |
| POST | `/api/auth/signup` | `{"username":"planner","password":"at-least-8-characters","email":"optional@example.com"}` |
| POST | `/api/auth/login` | `{"username":"planner","password":"..."}` |
| POST | `/api/auth/refresh` | No body; reads the HttpOnly refresh cookie |
| POST | `/api/auth/logout` | No body; blacklists the HttpOnly refresh cookie |

Signup and login set `aeropulse_access` and `aeropulse_refresh` HttpOnly cookies and return user metadata only. Use `credentials: "include"` in Next.js requests. When an API request returns 401, call `/api/auth/refresh`, then retry once.

Copy-ready Next.js middleware and API-client templates are in `docs/nextjs-auth/`. The Next.js server must have the same server-only `JWT_SIGNING_KEY` as Django so it can validate the signed short-lived access cookie before serving protected routes.

## Current endpoints

- `POST /api/imports/telemetry` - persists a CSV upload using Django storage and validates its header.
- `GET /api/fleet/overview` - fleet readiness summary.
- `GET /api/aircraft/{aircraft_id}` - aircraft profile.
- `GET /api/maintenance/queue` - priority ordered proposed work orders.
- `POST /api/work-orders` - creates a work order in `pending` state, awaiting human approval.

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

Read the latest stored import at `GET /api/iaf/fleet`. The returned payload attributes the source and does not claim the third-party data is first-party or real-time.
