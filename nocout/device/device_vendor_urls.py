from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.DeviceVendorList.as_view(), name='device_vendor_list'),
  url(r'^(?P<pk>\d+)/$', views.DeviceVendorDetail.as_view(), name='device_vendor_detail'),
  url(r'^new/$', views.DeviceVendorCreate.as_view(), name='device_vendor_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.DeviceVendorUpdate.as_view(), name='device_vendor_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.DeviceVendorDelete.as_view(), name='device_vendor_delete'),
  url(r'^DeviceVendorListingTable/', views.DeviceVendorListingTable.as_view(), name='DeviceVendorListingTable'),
)
