import django_filters
from django import forms

from .models import Device
from apps.commons.models import DeviceKind


class DeviceFilter(django_filters.FilterSet):
    kind = django_filters.MultipleChoiceFilter(
        choices=DeviceKind,
        field_name='device_model__kind',
        label='Тип устройства',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = Device
        fields = ('kind',)
