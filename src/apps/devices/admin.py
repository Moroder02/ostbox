from django.contrib import admin
from .models import DeviceModel, Device, Protocol

admin.site.register(DeviceModel)
admin.site.register(Device)
admin.site.register(Protocol)
