from django.conf.urls import patterns, url

from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceTypeFieldsList.as_view(), name='device_extra_field_list'),
  url(r'^(?P<pk>\d+)$', views.DeviceTypeFieldsDetail.as_view(), name='device_extra_field_detail'),
  url(r'^new/$', views.DeviceTypeFieldsCreate.as_view(), name='device_extra_field_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DeviceTypeFieldsUpdate.as_view(), name='device_extra_field_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DeviceTypeFieldsDelete.as_view(), name='device_extra_field_delete'),
)