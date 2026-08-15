from django.shortcuts import render

from .models import Device


def device_list(request):
    devices = Device.objects.all()
    context = {'devices': devices}
    return render(request, 'devices/device_list.html', context)

