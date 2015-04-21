from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
                       # page load
                       url(
                           r'^$',
                           views.SIAListing.as_view(),
                           name='traps'
                           ),
                       # current alarms
                       url(
                           r'^current$',
                           views.CurrentAlarmsListingTable.as_view(),
                           name='current-alarms'
                           ),
                       # clear alarms
                       url(
                           r'^clear$',
                           views.ClearAlarmsListingTable.as_view(),
                           name='clear-alarms'
                           ),
                       # history alarms
                       url(
                           r'^history$',
                           views.HistoryAlarmsListingTable.as_view(),
                           name='history-alarms'
                           ),
)
