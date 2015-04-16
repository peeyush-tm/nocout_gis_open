from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
               url(r'^$', views.DeviceFrequencyListing.as_view(), name='device_frequency_list'),
               url(r'^new/$', views.DeviceFrequencyCreate.as_view(), name='device_frequency_new'),
               url(r'^(?P<pk>\d+)/edit/$', views.DeviceFrequencyUpdate.as_view(), name='device_frequency_edit'),
               url(r'^(?P<pk>\d+)/delete/$', views.DeviceFrequencyDelete.as_view(), name='device_frequency_delete'),
               url(r'^devicefrequencylistingtable/$', views.DeviceFrequencyListingTable.as_view(), name='DeviceFrequencyListingTable'),
             )
