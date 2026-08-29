from django.shortcuts import render

from apps.devices.models import Protocol


def protocol_list(request):
    protocols = Protocol.objects.all()

    allowed_fields = [
        'name',
    ]

    obj_fields = [Protocol._meta.get_field(name) for name in allowed_fields]

    context = {
        'objects': protocols,
        'obj_fields': obj_fields,
    }

    return render(request, 'devices/device/device_list.html', context)
