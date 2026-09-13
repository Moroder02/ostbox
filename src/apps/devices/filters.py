import django_filters
from django import forms

from .models import Device, DiskModel, Disk
from apps.commons.models import DeviceKind, Protocol, OperatingSystem, Vendor


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


class DiskModelFilter(django_filters.FilterSet):
    vendor = django_filters.ModelMultipleChoiceFilter(
        queryset=Vendor.objects.filter(
            pk__in=DiskModel.objects.values_list('vendor_id', flat=True)
        ).order_by('name'),
        field_name='vendor',
        label='Вендор',
        widget=forms.SelectMultiple(attrs={
            'class': 'js-select2 form-select',
        })
    )

    class Meta:
        model = DiskModel
        fields = ('vendor',)


class DiskFilter(django_filters.FilterSet):
    vendor = django_filters.ModelMultipleChoiceFilter(
        queryset=Vendor.objects.filter(
            pk__in=DiskModel.objects.values_list('vendor_id', flat=True)
        ).order_by('name'),
        field_name='disk_model__vendor',
        label='Вендор',
        widget=forms.SelectMultiple(attrs={
            'class': 'js-select2 form-select',
        })
    )
    status = django_filters.MultipleChoiceFilter(
        choices=Disk.DiskStatus.choices,
        field_name='status',
        label='Статус',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )

    # # Для единичного выбора (радиокнопка)
    # status = django_filters.ChoiceFilter(
    #     choices=Disk.DiskStatus.choices,
    #     field_name='status',
    #     label='Статус',
    #     widget=forms.RadioSelect(attrs={
    #         'class': 'form-check-input',
    #         'type': 'radio',
    #     })
    # )
    class Meta:
        model = Disk
        fields = ('vendor', 'status')
