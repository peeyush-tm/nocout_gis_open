from django.conf.urls import patterns, url

from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceList.as_view(), name='device_list'),
  url(r'^(?P<pk>\d+)$', views.DeviceDetail.as_view(), name='device_detail'),
  url(r'^new/$', views.DeviceCreate.as_view(), name='device_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DeviceUpdate.as_view(), name='device_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DeviceDelete.as_view(), name='device_delete'),
)