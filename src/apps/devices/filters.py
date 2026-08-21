import django_filters
from django import forms

from .models import Vendor, ProductionCountry


class VendorFilter(django_filters.FilterSet):

    production_type = django_filters.ChoiceFilter(
        choices=ProductionCountry.choices,
        field_name='production',
        lookup_expr='iexact',
        empty_label='Любое',
        widget=forms.Select(attrs={'class': 'form-control mb-5'})
    )

    class Meta:
        model = Vendor
        fields = ('production_type',)
