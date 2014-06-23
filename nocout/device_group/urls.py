from django.conf.urls import patterns, url
from device_group import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceGroupList.as_view(), name='dg_list'),
  url(r'^(?P<pk>\d+)$', views.DeviceGroupDetail.as_view(), name='dg_detail'),
  url(r'^new/$', views.DeviceGroupCreate.as_view(), name='dg_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DeviceGroupUpdate.as_view(), name='dg_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DeviceGroupDelete.as_view(), name='dg_delete'),
  url(r'^devicegrouplistingtable/', views.DeviceGroupListingTable.as_view(), name='DeviceGroupListingTable'),
  url(r'^device_group_devices_wrt_organization/', views.device_group_devices_wrt_organization ),
)