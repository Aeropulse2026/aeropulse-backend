from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import requests

from fleet.globalmilitary import SOURCE_URL, parse_iaf_inventory
from fleet.models import ExternalFleetAircraft, ExternalFleetSnapshot


class Command(BaseCommand):
    help = "Fetch and normalize the public GlobalMilitary Indian Air Force inventory table."

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=20)

    def handle(self, *args, **options):
        try:
            response = requests.get(SOURCE_URL, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AeroPulse/0.1)",
                "Accept-Language": "en-US,en;q=0.9",
            },
                                    timeout=options["timeout"])
            response.raise_for_status()
            metadata, aircraft = parse_iaf_inventory(response.text)
        except (requests.RequestException, ValueError) as exc:
            raise CommandError(f"Import failed: {exc}") from exc

        with transaction.atomic():
            snapshot = ExternalFleetSnapshot.objects.create(source_url=SOURCE_URL, **metadata)
            ExternalFleetAircraft.objects.bulk_create([
                ExternalFleetAircraft(snapshot=snapshot, **record) for record in aircraft
            ])
        self.stdout.write(self.style.SUCCESS(f"Saved snapshot {snapshot.id} with {len(aircraft)} aircraft types."))
