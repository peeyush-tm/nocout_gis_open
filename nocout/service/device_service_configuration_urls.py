from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceServiceConfigurationList.as_view(), name='device_service_configuration_list'),
  url(r'^deviceserviceconfigurationlist/', views.DeviceServiceConfigurationListingTable.as_view(), name='DeviceServiceConfigurationListingTable'),
  url(r'^deleteddeviceserviceconfigurationlist/', views.DeletedDeviceServiceConfigurationListingTable.as_view(), name='DeletedDeviceServiceConfigurationListingTable'),
  url(r'^(?P<pk>\d+)/edit/$', views.DeviceServiceConfigurationUpdate.as_view(), name='deviceserviceconfiguration_edit'),
)