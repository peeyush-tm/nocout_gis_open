from django.conf.urls import patterns, url
from sitesearch import views

urlpatterns = patterns(
    '',
    url(r'^get_filters/$', views.DeviceGetFilters.as_view()),
)