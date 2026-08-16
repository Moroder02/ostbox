from django.shortcuts import render

from apps.devices.models import DeviceModel, Vendor


def model_list(request):
    device_models = DeviceModel.objects.all()
    context = {'device_models': device_models}
    return render(request, 'devices/device_models_list.html', context)


def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {'vendors': vendors}
    return render(request, 'devices/vendor_list.html', context)
