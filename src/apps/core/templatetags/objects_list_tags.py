from django import template
from django.db.models.fields.related import ManyToManyField

register = template.Library()


@register.filter
def get_field_value(obj, field_name):
    """Возвращает значение поля объекта по его строковому имени."""

    if not hasattr(obj, field_name):
        return ""

    value = getattr(obj, field_name)

    field = obj._meta.get_field(field_name)
    if isinstance(field, ManyToManyField):
        return ", ".join([str(item) for item in value.all()])

    return value


@register.inclusion_tag("core/object_filter.html")
def render_filter(context, filter_obj, title='Фильтрация'):
    
    return {
        'filter': filter_obj,
        'title': title,
        'request': context.get('request'),
    }