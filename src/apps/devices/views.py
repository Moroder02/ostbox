from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from .filters import DeviceFilter
from .models import Device


def device_list(request):
    device_filter = DeviceFilter(
        request.GET,
        queryset=Device.objects.all().select_related('device_model__vendor').order_by('device_model')
    )
    paginator = Paginator(device_filter.qs, settings.PAGE_SIZE)
    devices_page = paginator.page(1)
    context = {
        'objects': devices_page,
        'filter': device_filter,
        'devices': device_filter.qs,
        'selected_kinds': request.GET.getlist('kind'),
    }

    if request.htmx:
        return render(request, 'devices/device-list.html#filtering', context)
    return render(request, 'devices/device-list.html', context)


def get_devices(request):
    page = request.GET.get('page', 1)
    device_filter = DeviceFilter(
        request.GET,
        queryset=Device.objects.all().select_related('device_model__vendor').order_by('device_model')
    )
    paginator = Paginator(device_filter.qs, settings.PAGE_SIZE)
    context = {
        'objects': paginator.page(page)
    }
    return render(
        request,
        'devices/device-list.html#filtering',
        context
    )