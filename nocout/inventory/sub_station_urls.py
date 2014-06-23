from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.SubStationList.as_view(), name='sub_stations_list'),
  url(r'^(?P<pk>\d+)$', views.SubStationDetail.as_view(), name='sub_station_detail'),
  url(r'^new/$', views.SubStationCreate.as_view(), name='sub_station_new'),
  url(r'^edit/(?P<pk>\d+)$', views.SubStationUpdate.as_view(), name='sub_station_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.SubStationDelete.as_view(), name='sub_station_delete'),
  url(r'^SubStationlistingtable/', views.SubStationListingTable.as_view(), name='SubStationListingTable'),
)