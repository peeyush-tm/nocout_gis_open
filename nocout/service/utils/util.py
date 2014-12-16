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
    ds = ServiceDataSource.objects.all()
    for sds in ds:
        sds_name = sds.name.strip().lower()
        sds_alias = sds.alias.strip().title()
        if sds_name in SERVICE_DATA_SOURCE:
            SERVICE_DATA_SOURCE[sds_name]["display_name"] = sds_alias

        else:
            ds_to_append = {
                "display_name": sds_alias,
                "type": "table",
                "valuesuffix": " ",
                "valuetext": "",
                "formula": None,
                "show_min": False,
                "show_max": False
            }
            SERVICE_DATA_SOURCE.update({sds_name: ds_to_append})