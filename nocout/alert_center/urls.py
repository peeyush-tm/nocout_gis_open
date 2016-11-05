from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
	url(r'^((?P<page_type>\w+))_alert/(?P<data_source>\w+)/$', views.AlertCenterListing.as_view(), name='init_alert_listing'),
	url(r'^networklistingtable/', views.AlertListingTable.as_view(), name='AlertListingTable'),
	url(
		r'^(?P<page_type>\w+)_alert/(?P<data_source>\w+)/(?P<device_id>\w+)/$', 
		views.SingleDeviceAlertsInit.as_view(), 
		name='SingleDeviceAlertsInit'
	),
	url(
		r'^(?P<page_type>\w+)_alert/(?P<data_source>\w+)/(?P<device_id>\w+)/listing/$', 
		views.SingleDeviceAlertsListing.as_view(), 
		name='SingleDeviceAlertsListing_clone'
	),
	url(r'^network_detail/$', views.NetworkAlertDetailHeaders.as_view(), name='network_alert_details'),
	url(r'^network_detail_listing_table$', views.GetNetworkAlertDetail.as_view(), name='NetworkAlertDetails'),
	url(r'^(?P<page_type>\w+)_detail/$', views.AlertCenterListing.as_view(), name='customer_alert_details'),
	url(r'^customer_detail_listing_table/', views.AlertListingTable.as_view(), name='CustomerAlertDetails'),
	url(r'^all/listing/$', views.AllSiaListingTable.as_view(), name='all_alarms_listing'),
	url(r'^all/(?P<data_source>\w+)/$', views.AllSiaListing.as_view(), name='all_traps'),
	url(r'^planned_events/(?P<page_type>\w+)/$', views.PlannedEventsInit.as_view(), name='planned_events_init'),
	url(r'^planned_events/(?P<page_type>\w+)/listing/$', views.PlannedEventsListing.as_view(), name='planned_events_listing'),
)