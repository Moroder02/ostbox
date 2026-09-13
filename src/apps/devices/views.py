from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings

from .filters import DeviceFilter, DiskModelFilter, DiskFilter
from .models import Device, DiskModel, Disk


def device_list(request, kind=None):
    if kind:
        filters = DeviceFilter(
            request.GET,
            queryset=Device.objects.select_related(
                'device_model__vendor',
                'operating_system',
            ).prefetch_related(
                'management_protocols',
            ).filter(
                device_model__kind=kind
            )
        )
    else:
        filters = DeviceFilter(
            request.GET,
            queryset=Device.objects.select_related(
                'device_model__vendor',
                'operating_system',
            ).prefetch_related(
                'management_protocols'
            ).all()
        )
    paginator = Paginator(filters.qs, settings.PAGE_SIZE)
    page = request.GET.get('page', 1)
    context = {
        'kind': kind,
        'objects': paginator.page(page),
        'filter': filters,
        'select_kinds': request.GET.getlist('kind'),
        'selected_protocols': request.GET.getlist('protocol'),
        'selected_os': request.GET.getlist('operating_system'),
    }
    if request.htmx:
        return render(request, 'devices/device-list.html#filtering', context)
    return render(request, 'devices/device-list.html', context)


def disk_model_list(request):
    filters = DiskModelFilter(
        request.GET,
        queryset=DiskModel.objects.all().select_related('vendor'),
    )
    context = {
        'filter': filters,
        'disk_models': filters.qs,
        'total': len(list(filters.qs)),
        'selected_vendors': request.GET.getlist('vendor'),
    }
    if request.htmx:
        return render(request, 'devices/disk-model-list.html#filtering', context)
    return render(request, 'devices/disk-model-list.html', context)


def disk_list(request):
    filters = DiskFilter(
        request.GET,
        queryset=Disk.objects.all().select_related('disk_model', 'disk_model__vendor'),
    )
    context = {
        'filter': filters,
        'disks': filters.qs,
        'total': len(list(filters.qs)),
    }
    if request.htmx:
        return render(request, 'devices/disk-list.html#filtering', context)
    return render(request, 'devices/disk-list.html', context)
