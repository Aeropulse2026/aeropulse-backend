from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import requests

from squadron.bharat_rakshak import SOURCE_URL, parse_iaf_squadrons
from squadron.models import Squadron


class Command(BaseCommand):
    help = "Fetch and save IAF flying squadron names from Bharat-Rakshak."

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=20)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and report the records without saving them.",
        )

    def handle(self, *args, **options):
        try:
            response = requests.get(
                SOURCE_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; AeroPulse/0.1)",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=options["timeout"],
            )
            response.raise_for_status()
            records = parse_iaf_squadrons(response.text)
        except (requests.RequestException, ValueError) as exc:
            raise CommandError(f"Import failed: {exc}") from exc

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Parsed {len(records)} squadron records; no changes saved."))
            return

        created = updated = 0
        synced_at = timezone.now()
        with transaction.atomic():
            for record in records:
                squadron, was_created = Squadron.objects.get_or_create(
                    squadron_id=record["squadron_id"],
                    defaults={
                        **record,
                        "source_url": SOURCE_URL,
                        "source_last_synced_at": synced_at,
                    },
                )
                if was_created:
                    created += 1
                    continue
                squadron.name = record["name"]
                squadron.operational_role = record["operational_role"]
                squadron.source_url = SOURCE_URL
                squadron.source_last_synced_at = synced_at
                squadron.save(update_fields=[
                    "name", "operational_role", "source_url", "source_last_synced_at",
                ])
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"Saved {len(records)} squadrons ({created} created, {updated} updated)."
        ))
