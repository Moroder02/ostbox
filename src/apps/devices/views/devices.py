from django.shortcuts import render

from apps.devices.models import Device, DeviceModel
from apps.devices.filters import DeviceFilter

def device_list(request):
    devices = Device.objects.select_related('operating_system', 'device_model__vendor').all()
    device_filter = DeviceFilter(request.GET, queryset=devices)

    allowed_fields = [
        'device_model',
        'operating_system',
        'management_ip',
        'management_protocols'
    ]

    obj_fields = [Device._meta.get_field(name) for name in allowed_fields]

    context = {
        'objects': device_filter.qs,
        'obj_fields': obj_fields,
        'filter': device_filter,
        'selected_kinds': request.GET.getlist('kinds'),
    }
    if request.htmx:
        return render(request, 'core/object_list.html#filter', context)
    return render(request, 'core/object_list.html', context)


def model_list(request):
    device_models = DeviceModel.objects.all().select_related('vendor')
    context = {'device_models': device_models}
    return render(request, 'devices/device_model/device_models_list.html', context)
