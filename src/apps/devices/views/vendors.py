from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from apps.devices.forms.devices_forms import VendorForm
from apps.devices.models import Vendor


def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {
        'vendors': vendors,
        'form': VendorForm()
    }
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


# Как добавить подтверждение?
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        messages.success(request, 'Vendor deleted successfully.')
        return redirect('devices:vendor-list')

    return render(request, 'devices/vendors/vendor_confirm_delete.html', {'vendor': vendor})


def vendor_search(request):
    query = request.GET.get('search-vendor', '')
    vendors = Vendor.objects.filter(name__icontains=query)
    context = {'vendors': vendors}
    return render(request, 'devices/vendors/vendor_list.html#searching', context)
