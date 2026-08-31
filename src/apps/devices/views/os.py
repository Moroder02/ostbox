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


def os_list2(request):
    operating_systems = OperatingSystem.objects.select_related('vendor').all()
    os_filter = OSFilter(request.GET, queryset=operating_systems)
    
    allowed_fields = [
        'name',
        'family',
        'version',
        'vendor__country',
        # 'get_full_name'
    ]
    
    obj_fields = [OperatingSystem._meta.get_field(name) for name in allowed_fields]
    
    context = {
        'objects': os_filter.qs,
        'obj_fields': obj_fields,
        'selected_fields': request.GET.getlist('family'),
    }
    