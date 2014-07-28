from django.conf.urls import patterns, url
from device import views, api

urlpatterns = patterns('',
  url(r'^$', views.DeviceList.as_view(), name='device_list'),
  url(r'^(?P<pk>\d+)$', views.DeviceDetail.as_view(), name='device_detail'),
  url(r'^new/$', views.DeviceCreate.as_view(), name='device_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DeviceUpdate.as_view(), name='device_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DeviceDelete.as_view(), name='device_delete'),
  url(r'^stats/$', api.DeviceStatsApi.as_view()),
  url(r'^filter/$', api.DeviceFilterApi.as_view()),
  url(r'^lp_services/', api.LPServicesApi.as_view()),
  url(r'^lp_service_data/', api.FetchLPDataApi.as_view()),
  url(r'^treeview/$', views.create_device_tree, name='device_tree_view'),
  url(r'devicelistingtable/', views.DeviceListingTable.as_view(), name= 'DeviceListingTable'),
)
