# coding=utf-8
from django.conf.urls import patterns, url
from performance import views
from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
	url(r'^(?P<page_type>\w+)_live/$', views.LivePerformance.as_view(), name='performance_listing'),
	url(r'^liveperformancelistingtable/$', views.LivePerformanceListing.as_view(), name='LivePerformanceListing'),
	url(r'^get_topology/$', views.GetTopology.as_view(), name='DeviceTopology'),
	url(r'^get_telnet_ss/$', views.GetSSTelnet.as_view(), name='TelnetSSInfo'),
	url(r'^get_telnet_bs/$', views.GetBSTelnet.as_view(), name='TelnetBSInfo'),
	url(r'^EveryFiveMinDeviceStatus/$', views.EveryFiveMinDeviceStatus.as_view(), name='FiveMinuteStatus'),
	url(r'^get_topology/tool_tip/$', views.GetTopologyToolTip.as_view(), name='DeviceTopologyToolTip'),
	url(r'^(?P<page_type>\w+)_live/(?P<device_id>\w+)/$', views.GetPerfomance.as_view(), name='SingleDevicePerf'),
	url(r'^sector_dashboard/$', views.SectorDashboard.as_view(), name='spotDashboard'),
	url(r'^sector_dashboard/listing/$', views.SectorDashboardListing.as_view(), name='spotDashboardListing'),
	url(
		r'^get_inventory_device_status/(?P<page_type>\w+)/device/(?P<device_id>\d+)/$',
		views.InventoryDeviceStatus.as_view(),
		name='DeviceStatusUrl'
	),
	url(
		r'^get_inventory_service_data_sources/device/(?P<device_id>\d+)/$',
		views.InventoryDeviceServiceDataSource.as_view(), 
		name='get_service_data_source_url'
	),
	url(
		r'^service/(?P<service_name>\w+)/service_data_source/(?P<service_data_source_type>[-\w]+)/device/(?P<device_id>\d+)$',
		views.GetServiceTypePerformanceData.as_view(),
		name='GetServiceTypePerformanceData'
	),                       
	url(
		r'^custom_dashboard/(?P<custom_dashboard_id>\d+)/device/(?P<device_id>\d+)$',
		views.CustomDashboardPerformanceData.as_view(),
		name='CustomDashboardPerformanceData'
	),
	url(
		r'^listing/custom_dashboard/(?P<custom_dashboard_id>\d+)/device/(?P<device_id>\d+)$',
		views.CustomDashboardPerformanceListing.as_view(),
		name='CustomDashboardPerformanceListing'
	),
	url(r'^headers/single_perf_page/$', views.ServiceDataSourceHeaders.as_view(), name='ServiceDataSourceHeaders'),
	url(
		r'^listing/service/(?P<service_name>\w+)/service_data_source/(?P<service_data_source_type>[-\w]+)/device/(?P<device_id>\d+)$',
		views.ServiceDataSourceListing.as_view(),
		name='ServiceDataSourceListing'
	),
	url(
		r'^servicestatus/(?P<service_name>\w+)/service_data_source/(?P<service_data_source_type>[-\w]+)/device/(?P<device_id>\d+)/$',
		views.GetServiceStatus.as_view(),
		name='GetServiceStatus'
	),
	url(
		r'^servicedetail/(?P<service_name>\w+)/device/(?P<device_id>\d+)',
		views.DeviceServiceDetail.as_view(),
		name='DeviceServiceDetail'
	),
	url(
		r'get_severity_wise_status/',
		views.GetSeverityWiseStatus.as_view(),
		name='get_severity_wise_status'
	),
	url(r'^powerlisting/$', views.PowerStatusListing.as_view(), name='power_status_listing'),
	url(r'^powerstatus/$', views.PowerStatus.as_view(), name='power_status'),
	url(r'^send_power_sms/$', views.SendPowerSms.as_view(), name='power_sms'),
	url(r'^save_power_log/$', views.SavePowerLog.as_view(), name='save_power_log'),
	url(r'^init_device_reboot/$', views.InitDeviceReboot.as_view(), name='init_device_reboot')
)