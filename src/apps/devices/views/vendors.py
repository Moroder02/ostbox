from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from apps.devices.forms.devices_forms import VendorForm
from apps.devices.models import Vendor
from apps.devices.filters import VendorFilter


def vendor_list(request):
    vendors_filter = VendorFilter(
        request.GET,
        queryset=Vendor.objects.all()
    )
    context = {
        'filter': vendors_filter,
        'vendors': vendors_filter.qs,
        'form': VendorForm(),
        'selected_countries': request.GET.getlist('country'),
    }
    if request.htmx:
        return render(request, 'devices/vendors/vendor_list.html#searching', context)
    return render(request, 'devices/vendors/vendor_list.html', context)


def vendor_manage(request, pk=None):
    if pk:
        vendor = get_object_or_404(Vendor, pk=pk)
    else:
        vendor = None
    vendors = Vendor.objects.all()
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            vendor = form.save()
            action = "updated" if pk else "created"
            messages.success(request, f'Vendor {action} successfully.')
            return redirect('devices:vendor-detail', vendor.pk)
    else:
        form = VendorForm(instance=vendor)

    context = {
        'form': form,
        'vendor': vendor,
        'vendors': vendors
    }

    # Use the same template for both operations
    return render(request, 'devices/vendors/vendor_form.html', context)


def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    return render(request, 'devices/vendors/vendor_detail.html', {'vendor': vendor})


def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()

        # Проверяем, пришел ли запрос от htmx
        if request.headers.get('HX-Request'):
            return HttpResponse("", status=200)  # Возвращаем пустой ответ, htmx удалит строку

        messages.success(request, 'Vendor deleted successfully.')
        return redirect('devices:vendor-list')

    return render(request, 'devices/vendors/vendor_confirm_delete.html', {'vendor': vendor})

