from django.shortcuts import render

from apps.devices.models import OperatingSystem
from apps.devices.filters import OSFilter


def os_list(request):
    os_filter = OSFilter(request.GET, queryset=OperatingSystem.objects.select_related('vendor').all())
    context = {
        'filter': os_filter,
        'systems': os_filter.qs,
        'selected_families': request.GET.getlist('family'),
        'selected_countries': request.GET.getlist('vendor_country'),
    }
    if request.htmx:
        return render(request, 'devices/operating_systems/os_list.html#filter', context)
    return render(request, 'devices/operating_systems/os_list.html', context)
