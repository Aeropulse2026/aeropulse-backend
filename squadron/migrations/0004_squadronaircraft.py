from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("squadron", "0003_squadron_aircraft_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="SquadronAircraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aircraft_number", models.CharField(max_length=40, unique=True)),
                ("aircraft_name", models.CharField(max_length=120)),
                ("country_of_origin", models.CharField(max_length=80)),
                ("year_inducted", models.PositiveSmallIntegerField()),
                ("flight_hours", models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ("last_maintenance_on", models.DateField(blank=True, null=True)),
                ("next_maintenance_on", models.DateField(blank=True, null=True)),
                ("operational_role", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("squadron", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fleet_aircraft", to="squadron.squadron")),
            ],
            options={
                "ordering": ["squadron__squadron_id", "aircraft_number"],
            },
        ),
        migrations.AddIndex(
            model_name="squadronaircraft",
            index=models.Index(fields=["squadron", "next_maintenance_on"], name="sqd_ac_next_maint_idx"),
        ),
    ]
