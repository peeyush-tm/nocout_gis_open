from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
               url(r'^$', views.DeviceFrequencyListing.as_view(), name='device_frequency_list'),
               url(r'^new/$', views.DeviceFrequencyCreate.as_view(), name='device_frequency_new'),
               url(r'^edit/(?P<pk>\d+)$', views.DeviceFrequencyUpdate.as_view(), name='device_frequency_edit'),
               url(r'^delete/(?P<pk>\d+)$', views.DeviceFrequencyDelete.as_view(), name='device_frequency_delete'),
               url(r'^devicefrequencylistingtable/$', views.DeviceFrequencyListingTable.as_view(), name='DeviceFrequencyListingTable'),
             )
