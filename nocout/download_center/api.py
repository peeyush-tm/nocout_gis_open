import json
import logging
from django.http import HttpResponse
from django.views.generic.base import View
from device.models import DeviceTechnology
from download_center.models import CityCharterSettings

logger = logging.getLogger(__name__)


class FetchCityCharterSettings(View):
    """
        Fetch city charter settings from database.

        Args:
            technology (unicode): ID of technology.

        Returns:
            result (dict): Dictionary containing city charter settings.
                           For e.g.,
                                {
                                    "message": "Successfully fetched city charter settings.",
                                    "data": {
                                        "latency": "9809809",
                                        "jitter": "9870878",
                                        "uas": "",
                                        "rereg": "709709",
                                        "los": "49852452",
                                        "pd": "7098",
                                        "rogue_ss": "",
                                        "n_align": "",
                                        "technology": "PMP"
                                    },
                                    "success": 1
                                }

        URL:
            http://127.0.0.1:8000/city_charter_settings/get_current_cc_settings/?technology=p2p
    """
    def get(self, request):
        """
        Returns json containing city charter settings.
        """
        # Result dictionary to be returned as output of api.
        result = {
            "success": 0,
            "message": "Failed to fetch city charter settings.",
            "data": {
            }
        }

        # Get technology.
        technology = None
        try:
            technology = DeviceTechnology.objects.get(name__iexact=self.request.GET.get('technology', None))
        except Exception as e:
            logger.exception(e.message)

        if technology:
            # Fetch row corresponding to the 'technology' from 'download_center_citychartersettings'.
            row = None
            try:
                row = CityCharterSettings.objects.get(technology=technology)
            except Exception as e:
                logger.exception(e.message)

            if row:
                # Update record.
                result['data']['technology'] = technology.name
                result['data']['los'] = row.los
                result['data']['n_align'] = row.n_align
                result['data']['rogue_ss'] = row.rogue_ss
                result['data']['jitter'] = row.jitter
                result['data']['rereg'] = row.rereg
                result['data']['uas'] = row.uas
                result['data']['pd'] = row.pd
                result['data']['latency'] = row.latency
                result['data']['normal'] = row.normal
                result['message'] = "Successfully fetched city charter settings."
                result['success'] = 1

        return HttpResponse(json.dumps(result))