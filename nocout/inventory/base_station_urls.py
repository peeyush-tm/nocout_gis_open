from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.BaseStationList.as_view(), name='base_stations_list'),
  url(r'^(?P<pk>\d+)$', views.BaseStationDetail.as_view(), name='base_station_detail'),
  url(r'^new/$', views.BaseStationCreate.as_view(), name='base_station_new'),
  url(r'^edit/(?P<pk>\d+)$', views.BaseStationUpdate.as_view(), name='base_station_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.BaseStationDelete.as_view(), name='base_station_delete'),
  url(r'^BaseStationlistingtable/', views.BaseStationListingTable.as_view(), name='BaseStationListingTable'),
  url(r'^list/base_station/$', views.list_base_station, name='list-base_station'),
  url(r'^select/base_station/(?P<pk>\d+)/$', views.select_base_station, name='select-base_station'),
)
