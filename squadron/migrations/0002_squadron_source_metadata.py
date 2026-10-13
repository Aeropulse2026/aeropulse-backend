from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("squadron", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="squadron",
            name="aircraft_count",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="squadron",
            name="base",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AlterField(
            model_name="squadron",
            name="name",
            field=models.CharField(max_length=120),
        ),
        migrations.AddField(
            model_name="squadron",
            name="operational_role",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="squadron",
            name="source_last_synced_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="squadron",
            name="source_url",
            field=models.URLField(blank=True),
        ),
    ]
