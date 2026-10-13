from django.contrib import admin

from .models import AssetPart, MaintenanceTask


admin.site.register(MaintenanceTask)
admin.site.register(AssetPart)
