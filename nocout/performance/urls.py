from django.conf.urls import patterns, url
from performance import views
from performance.views import Get_Service_Type_Performance_Data

urlpatterns = patterns('',
	url(r'^(?P<page_type>\w+)_live/$', views.Live_Performance.as_view()),
	url(r'^liveperformancelistingtable/$', views.LivePerformanceListing.as_view(), name='LivePerformanceListing'),
	url(r'^(?P<page_type>\w+)_live/(?P<device_id>\w+)/$', views.Get_Perfomance.as_view()),
	url(r'^performance_dashboard/$', views.Performance_Dashboard.as_view()),
	url(r'^sector_dashboard/$', views.Sector_Dashboard.as_view()),
	url(r'^get_inventory_devices/(?P<page_type>\w+)$', views.Fetch_Inventory_Devices.as_view()),
	url(r'^get_inventory_device_status/(?P<page_type>\w+)/device/(?P<device_id>\d+)/$', views.Inventory_Device_Status.as_view()),
	url(r'^get_inventory_service_data_sources/(?P<page_type>\w+)/device/(?P<device_id>\d+)/$',
        views.Inventory_Device_Service_Data_Source.as_view()),
	url(r'^service_data_source/(?P<service_data_source_type>\w+)/(?P<page_type>\w+)/device/(?P<device_id>\d+)$', Get_Service_Type_Performance_Data.as_view())
)