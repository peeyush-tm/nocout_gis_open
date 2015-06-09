# -*- coding: utf-8 -*-

# project settings
from nocout.settings import SERVICE_DATA_SOURCE
from service.models import ServiceSpecificDataSource


class ServiceUtilsGateway:
    """
    This class works as a gateway between service utils & other apps
    """
    def service_data_sources(self):

        param1 = service_data_sources()

        return param1


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
    required_columns = ['service_data_sources__name',
                        'service_data_sources__alias',
                        'service_data_sources__chart_type',
                        'service_data_sources__valuesuffix',
                        'service_data_sources__valuetext',
                        'service_data_sources__show_min',
                        'service_data_sources__show_max',
                        'service_data_sources__show_gis',
                        'service_data_sources__show_performance_center',
                        'service_data_sources__is_inverted',
                        'service_data_sources__formula',
                        'service_data_sources__data_source_type',
                        'service_data_sources__warning',
                        'service_data_sources__critical',
                        'service_data_sources__chart_color',
                        'service__name',
                        'service__alias',
    ]


    # data sources queryset
    ds = ServiceSpecificDataSource.objects.filter().values(*required_columns)
    #ds = ServiceDataSource.objects.all().values(*required_columns)

    # service data sources dictionary
    SDS = SERVICE_DATA_SOURCE

    for sds in ds:
        formula = None
        if sds['service_data_sources__formula'] and len(sds['service_data_sources__formula'].strip()):
            formula = sds['service_data_sources__formula']

        sds_name = sds['service__name'].strip() + "_" +sds['service_data_sources__name'].strip()
        sds_alias = sds['service_data_sources__alias'].strip()

        ds_to_append = {
            'display_name': sds_alias,
            'type': sds['service_data_sources__chart_type'],
            'valuesuffix': sds['service_data_sources__valuesuffix'],
            'valuetext': sds['service_data_sources__valuetext'],
            'formula': formula,
            'show_min': sds['service_data_sources__show_min'],
            'show_max': sds['service_data_sources__show_max'],
            'show_gis': sds['service_data_sources__show_gis'],
            'show_performance_center': sds['service_data_sources__show_performance_center'],
            'is_inverted': sds['service_data_sources__is_inverted'],
            'data_source_type': 'String' if sds['service_data_sources__data_source_type'] else 'Numeric',
            'warning': sds['service_data_sources__warning'],
            'critical': sds['service_data_sources__critical'],
            'chart_color': sds['service_data_sources__chart_color'],
            'service_name': sds['service__name'],
            'service_alias': sds['service__alias'],
        }
        SDS.update({sds_name: ds_to_append})
    return SDS
