from django.conf.urls import patterns, url
from capacity_management import views


urlpatterns = patterns('',
    url(r'^daily_alert/(?P<alert_type>\w+)/$', views.get_daily_alerts),
    url(r'^status/backhaul/$', views.get_utilization_status),
    url(r'^status/sector/$', views.SectorStatusHeaders.as_view(), name="SectorStatusHeaders"),
    url(r'^status/sector/listing/$', views.SectorStatusListing.as_view(), name="SectorStatusListingClass"),
)