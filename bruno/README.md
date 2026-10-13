# AeroPulse Bruno collection

Open the `bruno/` folder in Bruno, then select either `local` or `supabase`
from the environment picker. Start the local API first with:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Authentication is currently disabled for API development, so Bruno requests do
not need a bearer token. The Supabase environment's `baseUrl` must be the URL
where this Django backend is deployed; it is not the Supabase dashboard or
project URL.

The upload request targets the generated fabricated telemetry CSV. For a smaller manual test file, select a different CSV in Bruno's file field.

The collection includes fleet overview, individual aircraft, telemetry import,
maintenance tasks, the imported IAF fleet snapshot, squadron records, and
individual squadron-aircraft records.

Create spare-part catalogue records first using `Maintenance / Create Spare
Part`. The catalogue supports full CRUD at `/api/maintenance/spare-parts/`.

`Maintenance / Create Aircraft Asset Part` registers an individually serialized
spare part against an internal aircraft. Set `aircraftId` to an existing
`Aircraft.aircraft_id` and `sparePartId` to an existing `InventoryPart.part_id`.
Use `List Aircraft Asset Parts` to view all assignments, or append
`?aircraft=YOUR_AIRCRAFT_ID` to filter the request URL.

The `Squadrons / List IAF Squadrons` request reads the locally stored squadron
records at `GET /api/fleet/squadrons/`. Populate those records once with
`uv run python manage.py scrape_iaf_squadrons`; the scraper is a management
command and is not triggered by Bruno or any API request.

Set `squadronId` to an existing `squadron_id` before using the `Create
Squadron Aircraft` request. Individual aircraft are available at
`GET /api/fleet/squadron-aircraft/`; filter by squadron with
`?squadron=YOUR_SQUADRON_ID`.

Suggested one-time IAF setup:

```bash
uv run python manage.py scrape_iaf_squadrons --dry-run
uv run python manage.py scrape_iaf_squadrons
```

After the import, run `List IAF Squadrons`, copy a returned `squadron_id` into
the environment's `squadronId` value, then use `Create Squadron Aircraft`.
