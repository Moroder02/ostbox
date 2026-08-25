from django.shortcuts import render

from apps.devices.models import OperatingSystem


def os_list(request):
    # systems = OperatingSystem.objects.select_related('vendor').all()
    systems = OperatingSystem.objects.all()
    return render(request, 'devices/operating_systems/os_list.html', {'systems': systems})
