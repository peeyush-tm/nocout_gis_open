from django.conf.urls import url
import api

urlpatterns = [
    url(r'^get_country_states/(?P<pk>\d+)/$', api.GetStatesForCountry.as_view()),
    url(r'^get_state_cities/(?P<pk>\d+)/$', api.GetCitiesForState.as_view()),
]
