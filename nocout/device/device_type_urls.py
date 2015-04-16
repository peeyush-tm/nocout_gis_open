from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceTypeList.as_view(), name='device_type_list'),
  url(r'^(?P<pk>\d+)/$', views.DeviceTypeDetail.as_view(), name='device_type_detail'),
  url(r'^new/$', views.DeviceTypeCreate.as_view(), name='device_type_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.DeviceTypeUpdate.as_view(), name='device_type_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.DeviceTypeDelete.as_view(), name='device_type_delete'),
  url(r'^devicetypelistingtable/$', views.DeviceTypeListingTable.as_view(), name='DeviceTypeListingTable'),

)
