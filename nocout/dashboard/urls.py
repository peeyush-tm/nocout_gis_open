from django.conf.urls import patterns, url

from dashboard import views


urlpatterns = patterns('',
    url(r'^settings/$', views.DashbaordSettingsListView.as_view(), name='dashboard-settings'),
    url(r'^settings/table/$', views.DashbaordSettingsListingTable.as_view(), name='dashboard-settings-table'),
)
