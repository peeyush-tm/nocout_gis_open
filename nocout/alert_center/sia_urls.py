from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
	# page load
	url(
		r'^$',
		views.SIAListing.as_view(),
		name='traps'
	),
	url(
		r'^listing/$',
		views.SIAListingTable.as_view(),
		name='snmp_alarms_listing'
	),
	url(
		r'^advance_filtering/$',
		views.GetSiaFiltersData.as_view(),
		name='sia_advance_filters_data'
	),
	url(
		r'^all/listing/$',
		views.AllSiaListingTable.as_view(),
		name='all_alarms_listing'
	),
	url(
		r'^all/(?P<data_source>\w+)/$',
		views.AllSiaListing.as_view(),
		name='all_traps'
	),
)
