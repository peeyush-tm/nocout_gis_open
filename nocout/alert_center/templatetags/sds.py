from service.utils.util import service_data_sources

from django import template

register = template.Library()

@register.filter(name='sds')
def sds(value):
    ##execute this globally
    SERVICE_DATA_SOURCE = service_data_sources()
    ##execute this globally

    if value:
        v = value.strip().lower()
        if v in SERVICE_DATA_SOURCE:
            return SERVICE_DATA_SOURCE[v]['display_name']
    return value