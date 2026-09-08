from django import template
from apps.commons.models import DeviceKind


register = template.Library()


@register.inclusion_tag('commons/partials/menu_items.html')
def device_kinds_items():
    return {'device_kinds_items': DeviceKind.choices}