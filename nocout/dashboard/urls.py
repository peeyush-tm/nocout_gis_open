from django.conf.urls import patterns, url

from dashboard import views


urlpatterns = patterns('',
    url(r'^settings/$', views.DashbaordSettingsListView.as_view(), name='dashboard-settings'),
    url(r'^settings/table/$', views.DashbaordSettingsListingTable.as_view(), name='dashboard-settings-table'),
    url(r'^settings/new/$', views.DashbaordSettingsCreateView.as_view(), name='dashboard-settings-new'),
    url(r'^settings/(?P<pk>\d+)/$', views.DashbaordSettingsDetailView.as_view(), name='dashboard-settings-detail'),
)
