from django.conf.urls import patterns, url
from capacity_management import views


urlpatterns = patterns('',
    url(r'^daily_alert/backhaul/$', views.get_daily_alerts),
    url(r'^daily_alert/sector/$', views.SectorAugmentationAlertsHerders.as_view(), name="SectorAugmentationAlertsHeaders"),
    url(r'^daily_alert/sector/listing/$', views.SectorAugmentationAlertsListing.as_view(), name="SectorAugmentationAlertsListing"),
    url(r'^status/backhaul/$', views.get_utilization_status),
    url(r'^status/sector/$', views.SectorStatusHeaders.as_view(), name="SectorStatusHeaders"),
    url(r'^status/sector/listing/$', views.SectorStatusListing.as_view(), name="SectorStatusListingClass"),
)