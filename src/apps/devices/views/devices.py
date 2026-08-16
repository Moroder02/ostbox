from django.shortcuts import render

from apps.devices.models import Device, DeviceModel


def device_list(request):
    devices = Device.objects.all().select_related('device_model')
    context = {'devices': devices}
    return render(request, 'devices/device/device_list.html', context)


def model_list(request):
    device_models = DeviceModel.objects.all().select_related('vendor')
    context = {'device_models': device_models}
    return render(request, 'devices/device_model/device_models_list.html', context)
