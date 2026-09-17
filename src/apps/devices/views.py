from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Sum, Q
from collections import Counter, defaultdict
from django.db.models import Prefetch

from .filters import DeviceFilter, DiskModelFilter, DiskFilter
from .models import Device, DiskModel, Disk, Processor, RAM, PhysicalNetworkPort
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
    # Оптимизированные prefetch с явными запросами
    disk_prefetch = Prefetch(
        'disks',
        queryset=Disk.objects.select_related('disk_model', 'disk_model__vendor')
    )

    processor_prefetch = Prefetch(
        'processors',
        queryset=Processor.objects.select_related(
            'processor_model',
            'processor_model__socket',
            'processor_model__vendor'
        )
    )

    ram_prefetch = Prefetch(
        'ram_modules',
        queryset=RAM.objects.select_related('ram_model')
    )

    port_prefetch = Prefetch(
        'physical_ports',
        queryset=PhysicalNetworkPort.objects.select_related('network_port_group')
    )

    device = get_object_or_404(
        Device.objects.select_related(
            'device_model',
            'device_model__vendor',
            'operating_system',
        ).prefetch_related(
            disk_prefetch,
            processor_prefetch,
            ram_prefetch,
            port_prefetch,
            'management_protocols',
        ),
        pk=pk,
    )

    # Агрегации на уровне Python, а не SQL
    disks = list(device.disks.all())
    disk_stats = {
        'total_nvme': sum(d.disk_model.capacity_gb for d in disks if d.disk_model.media_type == 'NVME'),
        'total_ssd': sum(d.disk_model.capacity_gb for d in disks if d.disk_model.media_type == 'SSD'),
        'total_hdd': sum(d.disk_model.capacity_gb for d in disks if d.disk_model.media_type == 'HDD'),
        'total_all': sum(d.disk_model.capacity_gb for d in disks),
    }

    processors = list(device.processors.all())
    cpu_stats = {
        'total_cores': sum(p.processor_model.cores for p in processors),
        'total_threads': sum(p.processor_model.threads for p in processors),
    }

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

    # ====== Блок ОЗУ: статистика и группировка ======
    ram_modules = list(device.ram_modules.all())

    speeds = [m.memory_speed_mts for m in ram_modules if m.memory_speed_mts]
    latencies = [m.ram_model.latency_cl for m in ram_modules if m.ram_model.latency_cl]
    unique_models = len({m.ram_model_id for m in ram_modules})

    ram_stats = {
        'total_count': len(ram_modules),
        'total_gb': sum(m.capacity_gb for m in ram_modules),
        # по типам памяти (оставляем — может пригодиться в будущем)
        'ddr3_gb': sum(m.capacity_gb for m in ram_modules if m.memory_type == 'DDR3'),
        'ddr4_gb': sum(m.capacity_gb for m in ram_modules if m.memory_type == 'DDR4'),
        'ddr5_gb': sum(m.capacity_gb for m in ram_modules if m.memory_type == 'DDR5'),
        'other_gb': sum(m.capacity_gb for m in ram_modules
                        if m.memory_type not in ('DDR3', 'DDR4', 'DDR5')),
        # по статусам
        'active': sum(1 for m in ram_modules if m.status == 'ACTIVE'),
        'spare': sum(1 for m in ram_modules if m.status == 'SPARE'),
        'faulty': sum(1 for m in ram_modules if m.status == 'FAULTY'),
        'retired': sum(1 for m in ram_modules if m.status == 'RETIRED'),
        # новые полезные метрики
        'min_speed': min(speeds) if speeds else 0,
        'max_speed': max(speeds) if speeds else 0,
        'avg_cl': round(sum(latencies) / len(latencies)) if latencies else None,
        'min_cl': min(latencies) if latencies else None,
        'max_cl': max(latencies) if latencies else None,
        'unique_models': unique_models,
    }

    # Группировка по модели RAMModel (для rowspan в таблице)
    ram_groups_dict = {}
    for ram in ram_modules:
        model = ram.ram_model
        if model not in ram_groups_dict:
            ram_groups_dict[model] = {
                'model': model,
                'modules': [],
                'count': 0,
                'total_gb': 0,
            }
        ram_groups_dict[model]['modules'].append(ram)
        ram_groups_dict[model]['count'] += 1
        ram_groups_dict[model]['total_gb'] += ram.capacity_gb

    ram_groups = list(ram_groups_dict.items())
    # ================================================

    context = {
        'device': device,
        'disk_stats': disk_stats,
        'cpu_stats': cpu_stats,
        'port_stats': port_stats,
        'port_groups': port_groups,
        'ram_stats': ram_stats,  # <-- добавлено
        'ram_groups': ram_groups,  # <-- добавлено
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
