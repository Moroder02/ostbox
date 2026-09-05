import django_filters
from django import forms

from .models import Device
from apps.commons.models import DeviceKind, Protocol, OperatingSystem


class DeviceFilter(django_filters.FilterSet):
    kind = django_filters.MultipleChoiceFilter(
        choices=DeviceKind,
        field_name='device_model__kind',
        label='Тип устройства',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )
    protocol = django_filters.ModelMultipleChoiceFilter(
        queryset=Protocol.objects.all(),
        field_name='management_protocols',
        label='Протоколы подключения',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )
    operating_system = django_filters.ModelMultipleChoiceFilter(
        queryset=OperatingSystem.objects.all(),
        field_name='operating_system',
        label='Операционные системы',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )
    class Meta:
        model = Device
        fields = ('kind', 'protocol')