from django.shortcuts import render, redirect

from apps.devices.models import Device


def device_list(request):
    devices = Device.objects.all()
    context = {'devices': devices}
    return render(request, 'devices/device_list.html', context)
