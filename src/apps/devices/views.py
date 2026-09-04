from django.shortcuts import render
from .filters import DeviceFilter
from .models import Device


def device_list(request):
    device_filter = DeviceFilter(
        request.GET,
        queryset=Device.objects.all()
    )
    context = {
        'filter': device_filter,
        'devices': device_filter.qs,
        'selected_kinds': request.GET.getlist('kind'),
    }

    if request.htmx:
        return render(request, 'devices/device-list.html#filtering', context)
    return render(request, 'devices/device-list.html', context)
