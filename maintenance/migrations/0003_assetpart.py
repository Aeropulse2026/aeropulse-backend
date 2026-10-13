from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("fleet", "0004_userprofile"),
        ("maintenance", "0002_maintenancetask_squadron"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetPart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("serial_number", models.CharField(max_length=80, unique=True)),
                ("installed_location", models.CharField(blank=True, max_length=100)),
                ("installed_on", models.DateField(blank=True, null=True)),
                ("last_maintained_on", models.DateField(blank=True, null=True)),
                ("next_maintenance_on", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("installed", "Installed"), ("in_service", "In service"), ("under_maintenance", "Under maintenance"), ("retired", "Retired")], default="installed", max_length=24)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("aircraft", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="asset_parts", to="fleet.aircraft")),
                ("inventory_part", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="asset_assignments", to="fleet.inventorypart")),
            ],
            options={
                "ordering": ["aircraft__aircraft_id", "serial_number"],
            },
        ),
        migrations.AddIndex(
            model_name="assetpart",
            index=models.Index(fields=["aircraft", "status", "next_maintenance_on"], name="assetpart_aircraft_due_idx"),
        ),
    ]
