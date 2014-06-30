from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.DevicePortList.as_view(), name='device_ports_list'),
  url(r'^(?P<pk>\d+)$', views.DevicePortDetail.as_view(), name='device_port_detail'),
  url(r'^new/$', views.DevicePortCreate.as_view(), name='device_port_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DevicePortUpdate.as_view(), name='device_port_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DevicePortDelete.as_view(), name='device_port_delete'),
  url(r'^deviceportlistingtable/', views.DevicePortListingTable.as_view(), name='DevicePortListingTable'),
)