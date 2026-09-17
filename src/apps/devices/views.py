from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Sum, Q
from collections import Counter, defaultdict

from .filters import DeviceFilter, DiskModelFilter, DiskFilter
from .models import Device, DiskModel, Disk
from apps.commons.models import DeviceKind


def device_list(request, kind=None):
    queryset = Device.objects.select_related(
        'device_model',
        'device_model__vendor',
        'operating_system',
    ).prefetch_related(
        'management_protocols',
    ).order_by('id')
    kind_display = None
    if kind:
        queryset = queryset.filter(device_model__kind=kind)
        kind_display = dict(DeviceKind.choices)[kind]
    filters = DeviceFilter(request.GET, queryset=queryset, kind=kind)
    paginator = Paginator(filters.qs, settings.PAGE_SIZE)
    page = request.GET.get('page', 1)
    context = {
        'kind': kind,
        'objects': paginator.page(page),
        'filter': filters,
        'title': kind_display,
    }
    if request.htmx:
        return render(request, 'devices/device/device-list.html#filtering', context)
    return render(request, 'devices/device/device-list.html', context)


def device_detail(request, pk):
    device = get_object_or_404(
        Device.objects.select_related(
            'device_model',
            'device_model__vendor',
            'operating_system',
        ).prefetch_related(
            'disks__disk_model',
            'disks__disk_model__vendor',
            'physical_ports__network_port_group',
            'management_protocols',
            'processors__processor_model__socket',
            'processors__processor_model',
        ),
        pk=pk,
    )
    disk_stats = device.disks.aggregate(
        total_nvme=Sum('disk_model__capacity_gb', filter=Q(disk_model__media_type='NVME')),
        total_ssd=Sum('disk_model__capacity_gb', filter=Q(disk_model__media_type='SSD')),
        total_hdd=Sum('disk_model__capacity_gb', filter=Q(disk_model__media_type='HDD')),
        total_all=Sum('disk_model__capacity_gb'),
    )
    cpu_stats = device.processors.aggregate(
        total_cores=Sum('processor_model__cores'),
        total_threads=Sum('processor_model__threads'),
    )
    ports = list(device.physical_ports.all())  # один запрос, результат в кэше
    status_counter = Counter(p.status for p in ports)
    port_stats = {
        'total': len(ports),
        'active': status_counter.get('active', 0),
        'inactive': status_counter.get('inactive', 0),
        'disabled': status_counter.get('disabled', 0),
        'reserved': status_counter.get('reserved', 0),
        'faulty': status_counter.get('faulty', 0),
    }
    # Группировка по NetworkPortGroup
    port_groups_dict = {}
    for port in ports:
        group = port.network_port_group
        if group not in port_groups_dict:
            port_groups_dict[group] = {
                'group': group,
                'ports': [],
                'count': 0,
            }
        port_groups_dict[group]['ports'].append(port)
        port_groups_dict[group]['count'] += 1

    # Преобразуем в список кортежей для шаблона
    port_groups = list(port_groups_dict.items())

    context = {
        'device': device,
        'disk_stats': disk_stats,
        'cpu_stats': cpu_stats,
        'port_stats': port_stats,
        'port_groups': port_groups,
    }
    return render(request, 'devices/device/device_detail.html', context)


def disk_list(request):
    filters = DiskFilter(
        request.GET,
        queryset=Disk.objects.all().select_related('disk_model', 'disk_model__vendor'),
    )
    context = {
        'filter': filters,
        'disks': filters.qs,
        # 'total': len(list(filters.qs)),
    }
    if request.htmx:
        return render(request, 'devices/disk/disk-list.html#filtering', context)
    return render(request, 'devices/disk/disk-list.html', context)


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
        return render(request, 'devices/disk/disk-model-list.html#filtering', context)
    return render(request, 'devices/disk/disk-model-list.html', context)
