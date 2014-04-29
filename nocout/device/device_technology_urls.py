from django.conf.urls import patterns, url

from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceTechnologyList.as_view(), name='device_technology_list'),
  url(r'^(?P<pk>\d+)$', views.DeviceTechnologyDetail.as_view(), name='device_technology_detail'),
  url(r'^new/$', views.DeviceTechnologyCreate.as_view(), name='device_technology_new'),
  url(r'^edit/(?P<pk>\d+)$', views.DeviceTechnologyUpdate.as_view(), name='device_technology_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.DeviceTechnologyDelete.as_view(), name='device_technology_delete'),
)