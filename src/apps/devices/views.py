from django.shortcuts import render


def device_list(request):
    context = {}
    return render(request, 'devices/device-list.html', context)