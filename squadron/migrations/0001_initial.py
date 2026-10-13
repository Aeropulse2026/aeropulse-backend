from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Squadron",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("squadron_id", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("base", models.CharField(max_length=80)),
                ("aircraft_count", models.PositiveSmallIntegerField(default=0)),
            ],
        ),
    ]
