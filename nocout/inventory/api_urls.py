from django.conf.urls import url, include
from rest_framework import routers
from inventory import api

router = routers.DefaultRouter()
router.register(r'antennas', api.AntennaViewSet, base_name='antenna')
router.register(r'backhauls', api.BackhaulViewSet, base_name='backhaul')
router.register(r'sectors', api.SectorViewSet, base_name='sector')
router.register(r'basestations', api.BaseStationViewSet, base_name='basestation')
router.register(r'substations', api.SubStationViewSet, base_name='substation')
router.register(r'customers', api.CustomerViewSet, base_name='customer')
router.register(r'circuits', api.CircuitViewSet, base_name='circuit')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
