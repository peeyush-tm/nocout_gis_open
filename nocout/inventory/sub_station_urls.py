from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.SubStationList.as_view(), name='sub_stations_list'),
  url(r'^(?P<pk>\d+)/$', views.SubStationDetail.as_view(), name='sub_station_detail'),
  url(r'^new/$', views.SubStationCreate.as_view(), name='sub_station_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.SubStationUpdate.as_view(), name='sub_station_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.SubStationDelete.as_view(), name='sub_station_delete'),
  url(r'^SubStationlistingtable/', views.SubStationListingTable.as_view(), name='SubStationListingTable'),
  url(r'^list/sub_station/$', views.list_sub_station, name='list-sub_station'),
  url(r'^select/sub_station/(?P<pk>\d+)/$', views.select_sub_station, name='select-sub_station'),
)
