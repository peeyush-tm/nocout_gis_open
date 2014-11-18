from django.conf.urls import patterns, url

from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceTypeFieldsList.as_view(), name='device_extra_field_list'),
  url(r'^(?P<pk>\d+)/$', views.DeviceTypeFieldsDetail.as_view(), name='device_extra_field_detail'),
  url(r'^new/$', views.DeviceTypeFieldsCreate.as_view(), name='device_extra_field_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.DeviceTypeFieldsUpdate.as_view(), name='device_extra_field_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.DeviceTypeFieldsDelete.as_view(), name='device_extra_field_delete'),
  url(r'^devicetypefieldslist/', views.DeviceTypeFieldsListingTable.as_view(), name='DeviceTypeFieldsListingTable'),

)
