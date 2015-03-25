from django.conf.urls import patterns, url
from alert_center import sia


urlpatterns = patterns('',
                       # page load
                       url(
                           r'^$',
                           sia.SIAListing.as_view(),
                           name='traps'
                           ),
                       # current alarms
                       url(
                           r'^current$',
                           sia.CurrentAlarmsListingTable.as_view(),
                           name='current-alarms'
                           ),
                       # clear alarms
                       url(
                           r'^clear$',
                           sia.ClearAlarmsListingTable.as_view(),
                           name='clear-alarms'
                           ),
                       # history alarms
                       url(
                           r'^history$',
                           sia.HistoryAlarmsListingTable.as_view(),
                           name='history-alarms'
                           ),
)
