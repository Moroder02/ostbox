from django.contrib import admin

from .models import DiskModel, Disk

admin.site.register(DiskModel)
admin.site.register(Disk)
