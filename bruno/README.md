# AeroPulse Bruno collection

Open the `bruno/` folder in Bruno, then select either `local` or `supabase` from the environment picker.

Set `token` to a Django API bearer token. Create one with `uv run python manage.py drf_create_token YOUR_USERNAME`. The Supabase environment's `baseUrl` must be the URL where this Django backend is deployed; it is not the Supabase dashboard or project URL.

The upload request targets the generated fabricated telemetry CSV. For a smaller manual test file, select a different CSV in Bruno's file field.
