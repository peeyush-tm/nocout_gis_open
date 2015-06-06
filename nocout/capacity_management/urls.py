from django.conf.urls import patterns, url
from capacity_management import views


urlpatterns = patterns('',
    url(r'^daily_alert/backhaul/$', views.BackhaulAugmentationAlertsHeaders.as_view(), name="BackhaulAugmentationAlertsHeaders"),
    url(r'^daily_alert/sector/$', views.SectorAugmentationAlertsHerders.as_view(), name="SectorAugmentationAlertsHeaders"),
    url(r'^daily_alert/backhaul/listing/$', views.BackhaulAugmentationAlertsListing.as_view(), name="BackhaulAugmentationAlertsListing"),
    url(r'^daily_alert/sector/listing/$', views.SectorAugmentationAlertsListing.as_view(), name="SectorAugmentationAlertsListing"),
    url(r'^status/sector/$', views.SectorStatusHeaders.as_view(), name="SectorStatusHeaders"),
    url(r'^status/sector/listing/$', views.SectorStatusListing.as_view(), name="SectorStatusListingClass"),
    url(r'^status/backhaul/$', views.BackhaulStatusHeaders.as_view(), name="BackhaulStatusHeaders"),
    url(r'^status/backhaul/listing/$', views.BackhaulStatusListing.as_view(), name="BackhaulStatusListingClass"),
)