from django.conf.urls import patterns, url

from dashboard import views


urlpatterns = patterns('',
    url(r'^settings/$', views.DashbaordSettingsListView.as_view(), name='dashboard-settings'),
    url(r'^settings/table/$', views.DashbaordSettingsListingTable.as_view(), name='dashboard-settings-table'),
    url(r'^settings/new/$', views.DashbaordSettingsCreateView.as_view(), name='dashboard-settings-new'),
    url(r'^settings/(?P<pk>\d+)/$', views.DashbaordSettingsDetailView.as_view(), name='dashboard-settings-detail'),
    url(r'^settings/(?P<pk>\d+)/edit/$', views.DashbaordSettingsUpdateView.as_view(), name='dashboard-settings-update'),
    url(r'^settings/(?P<pk>\d+)/delete/$', views.DashbaordSettingsDeleteView.as_view(), name='dashboard-settings-delete'),

    url(r'^rf-performance/wimax/$', views.WiMAX_Performance_Dashboard.as_view(), name='dashboard-rf-performance-wimax'),
    url(r'^rf-performance/pmp/$', views.PMP_Performance_Dashboard.as_view(), name='dashboard-rf-performance-pmp'),
    url(r'^rf-performance/ptp/$', views.PTP_Performance_Dashboard.as_view(), name='dashboard-rf-performance-ptp'),
    url(r'^rf-performance/ptp-bh/$', views.PTPBH_Performance_Dashboard.as_view(), name='dashboard-rf-performance-ptp-bh'),
)
