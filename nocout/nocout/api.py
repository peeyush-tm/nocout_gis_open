from device.models import Country, State
from rest_framework.views import APIView
from rest_framework.response import Response
from dashboard.utils import get_unused_dashboards


class GetStatesForCountry(APIView):
    """
    Fetch states corresponding to the selected country.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_country_states/1/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                          For e.g.,
                                [
                                    {
                                        "id": 1,
                                        "name": "Andhra Pradesh"
                                    },
                                    {
                                        "id": 2,
                                        "name": "Arunachal Pradesh"
                                    },
                                    {
                                        "id": 3,
                                        "name": "Assam"
                                    },
                                    {
                                        "id": 4,
                                        "name": "Bihar"
                                    },
                                    {
                                        "id": 5,
                                        "name": "Chhattisgarh"
                                    },
                                ]
        """
        country_id = pk

        # Response of api.
        result = list()

        # Country object.
        country = None
        if country_id:
            country = Country.objects.filter(id=country_id)

        # Fetch states associated with the selected country.
        if country:
            states = country[0].state_set.all()

            result = [{'id': value.id,
                       'name': value.state_name} for value in states]

        return Response(result)


class GetCitiesForState(APIView):
    """
    Fetch cities corresponding to the selected state.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_state_cities/1/"
    """

    def get(self, request, pk):
        """
        Processing API request.
        Args:
            pk (unicode): Selected option value.

        Returns:
            result (str): JSON formatted response.
                         For e.g.,
                            [
                                {
                                    "id": 1,
                                    "name": "Adilabad"
                                },
                                {
                                    "id": 2,
                                    "name": "Adoni"
                                },
                                {
                                    "id": 3,
                                    "name": "Amadalavalasa"
                                },
                                {
                                    "id": 4,
                                    "name": "Amalapuram"
                                },
                                {
                                    "id": 5,
                                    "name": "Anakapalle"
                                }
                            ]
        """
        state_id = pk

        # Response of api.
        result = list()

        # State object.
        state = None
        if state_id:
            state = State.objects.filter(id=state_id)

        # Fetch cities associated with the selected state.
        if state:
            states = state[0].city_set.all()

            result = [{'id': value.id,
                       'name': value.city_name} for value in states]

        return Response(result)

class GetUnusedDashboard(APIView):
    """
    Get dashboards which have no defined setting for them
    on basis of device tech and device type
    """
    def get(self, request, device_type=None):
        result = []

        if not device_type:
            return Response(result)

        result = get_unused_dashboards(device_type_id=device_type)

        for dashboard in result:
            dashboard.update({
                    'name': dashboard['dashboard_name'],
                    'alias': dashboard['dashboard_name'],
                    'id': dashboard['dashboard_name']
                })

        return Response(result)
