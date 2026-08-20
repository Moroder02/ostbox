from django import forms
from apps.devices.models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'production', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'production': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
        }
