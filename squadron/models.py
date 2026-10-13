from django.conf import settings
from django.db import models

# Create your models here.

class Squadron(models.Model):
    squadron_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    base = models.CharField(max_length=80)
    aircraft_count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name
