# -*- coding: utf-8 -*-

# project settings
from nocout.settings import SERVICE_DATA_SOURCE

from nocout.utils.util import cache_for

from service.models import ServiceDataSource


@cache_for(300)
def service_data_sources():
    """ Fetch service data sources information in a dictionary

        Returns:
           - SDS (dict) - dictionary containing data source information for e.g.
                                                {
                                                    u'commanded_rx_power':
                                                                        {
                                                                            'show_min': False,
                                                                            'warning': u'',
                                                                            'display_name': u'Aprxpower',
                                                                            'show_gis': False,
                                                                            'valuesuffix': u'seconds',
                                                                            'data_source_type': 'String',
                                                                            'critical': u'',
                                                                            'show_max': False,
                                                                            'chart_color': u'#70AFC4',
                                                                            'formula': None,
                                                                            'type': u'table',
                                                                            'valuetext': u'seconds'
                                                                        },
                                                    u'low_pri_dl_cir': {
                                                                            'show_min': False,
                                                                            'warning': u'',
                                                                            'display_name': u'lowprioritydownlinkcir',
                                                                            'show_gis': False,
                                                                            'valuesuffix': u'seconds',
                                                                            'data_source_type': 'String',
                                                                            'critical': u'',
                                                                            'show_max': False,
                                                                            'chart_color': u'#70AFC4',
                                                                            'formula': None,
                                                                            'type': u'table',
                                                                            'valuetext': u'seconds'
                                                                        }
                                                }
    """

    # fields need to show on tool-tip
    required_columns = ['name',
                        'alias',
                        'chart_type',
                        'valuesuffix',
                        'valuetext',
                        'show_min',
                        'show_max',
                        'show_gis',
                        'formula',
                        'data_source_type',
                        'warning',
                        'critical',
                        'chart_color']

    # data sources queryset
    ds = ServiceDataSource.objects.all().values(*required_columns)

    # service data sources dictionary
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
            'show_gis': sds['show_gis'],
            'data_source_type': 'String' if sds['data_source_type'] else 'Numeric',
            'warning': sds['warning'],
            'critical': sds['critical'],
            'chart_color': sds['chart_color']
        }
        SDS.update({sds_name: ds_to_append})
    return SDS