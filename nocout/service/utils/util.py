# -*- coding: utf-8 -*-

# project settings
from nocout.settings import SERVICE_DATA_SOURCE

from nocout.utils.util import cache_for

from service.models import ServiceDataSource

@cache_for(300)
def service_data_sources():
    """

    :return: dictionary of data sources
    """
    required_columns = ['name', 'alias', 'chart_type', 'valuesuffix', 'valuetext', 'show_min', 'show_max', 'formula', 'data_source_type', 'warning', 'critical', 'chart_color']
    ds = ServiceDataSource.objects.all().values(*required_columns)
    SDS = SERVICE_DATA_SOURCE
    for sds in ds:
        formula = None
        if sds['formula'] and len(sds['formula'].strip()):
            formula = sds['formula']
        sds_name = sds['name'].strip().lower()
        sds_alias = sds['alias']
        ds_to_append = {
            'display_name': sds_alias,
            'type': sds['chart_type'],
            'valuesuffix': sds['valuesuffix'],
            'valuetext': sds['valuetext'],
            'formula': formula,
            'show_min': sds['show_min'],
            'show_max': sds['show_max'],
            'data_source_type': 'String' if sds['data_source_type'] else 'Numeric',
            'warning': sds['warning'],
            'critical': sds['critical'],
            'chart_color': sds['chart_color']
        }
        SDS.update({sds_name: ds_to_append})
    return SDS