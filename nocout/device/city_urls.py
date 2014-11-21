from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.CityListing.as_view(), name='city_list'),
  url(r'^(?P<pk>\d+)/$', views.CityDetail.as_view(), name='city_detail'),
  url(r'^new/$', views.CityCreate.as_view(), name='city_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.CityUpdate.as_view(), name='city_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.CityDelete.as_view(), name='city_delete'),
  url(r'^citylistingtable/$', views.CityListingTable.as_view(), name='CityListingTable'),
)
