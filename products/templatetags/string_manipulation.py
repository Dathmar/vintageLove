from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def trunk(value, trunk_len):
    if len(value) <= trunk_len:
        return value
    else:
        return ' '.join(value[:trunk_len+1].split(' ')[0:-1]) + '...'
