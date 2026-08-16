from django import forms
from apps.devices.models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
