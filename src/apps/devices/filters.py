import django_filters
from django import forms
from django.db.models import Q

from .models import Vendor, ProductionCountry, Countries


class VendorFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method='filter_search',
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск вендора..',
        })
    )
    production_type = django_filters.ChoiceFilter(
        choices=ProductionCountry.choices,
        field_name='production',
        lookup_expr='iexact',
        empty_label='Любое',
        widget=forms.Select(attrs={'class': 'form-control mb-3'})
    )

    country = django_filters.MultipleChoiceFilter(
        choices=Countries.choices,
        field_name='country',
        label='Страна',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = Vendor
        fields = ('search', 'production_type', 'country')

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(country__icontains=value)
        )
