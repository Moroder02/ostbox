from django.shortcuts import render

from .models import Device, DeviceModel, Vendor


def device_list(request):
    devices = Device.objects.all()
    context = {'devices': devices}
    return render(request, 'devices/device_list.html', context)


def model_list(request):
    device_models = DeviceModel.objects.all()
    context = {'device_models': device_models}
    return render(request, 'devices/device_models_list.html', context)


def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {'vendors': vendors}
    return render(request, 'devices/vendor_list.html', context)
