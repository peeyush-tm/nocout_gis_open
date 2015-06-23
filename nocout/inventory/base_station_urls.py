from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.BaseStationList.as_view(), name='base_stations_list'),
  url(r'^(?P<pk>\d+)/$', views.BaseStationDetail.as_view(), name='base_station_detail'),
  url(r'^new/$', views.BaseStationCreate.as_view(), name='base_station_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.BaseStationUpdate.as_view(), name='base_station_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.BaseStationDelete.as_view(), name='base_station_delete'),
  url(r'^BaseStationlistingtable/', views.BaseStationListingTable.as_view(), name='BaseStationListingTable'),
  url(r'^select2/elements/$', views.SelectBaseStationListView.as_view(), name='select2-base-station-elements'),
  url(r'^(?P<bs_id>\d+)/l2_reports/$', views.CircuitL2Report_Init.as_view(), name='circuit_l2_report'),
  url(r'^L2listingtable/(?P<bs_id>\d+)/$', views.BSL2ReportListingTable.as_view(), name='BSL2ReportListingTable'),
  url(r'^(?P<bs_id>\d+)/l2_reports/create/$', views.BSL2ReportCreate.as_view(), name='bs_l2_report_create'),
  url(r'^upload/(?P<bs_id>\d+)/(?P<report_type>)$', views.get_l2report_count, name='bs_get_l2report_count'),
  url(r'^(?P<bs_id>\d+)/l2_reports/(?P<l2_id>\d+)/delete/$', views.BsL2ReportDelete.as_view(), name='bs_l2_report_delete'),
)
