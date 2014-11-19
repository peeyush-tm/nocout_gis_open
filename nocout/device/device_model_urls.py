from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceModelList.as_view(), name='device_model_list'),
  url(r'^(?P<pk>\d+)/$', views.DeviceModelDetail.as_view(), name='device_model_detail'),
  url(r'^new/$', views.DeviceModelCreate.as_view(), name='device_model_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.DeviceModelUpdate.as_view(), name='device_model_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.DeviceModelDelete.as_view(), name='device_model_delete'),
  url(r'^devicemodellistingtable/', views.DeviceModelListingTable.as_view(), name='DeviceModelListingTable'),
)
