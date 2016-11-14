from django.conf.urls import url
import api

urlpatterns = [
    url(r'^get_country_states/(?P<pk>\d+)/$', api.GetStatesForCountry.as_view(), name='get_states_for_country'),
    url(r'^get_state_cities/(?P<pk>\d+)/$', api.GetCitiesForState.as_view(), name='get_cities_for_state'),
    url(r'^get_unused_dashboard/(?P<device_type>\d+)/$', api.GetUnusedDashboard.as_view(), name='get_unused_dashboard')
]
