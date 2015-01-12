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

    url(r'^mfr-dfr-reports/$', views.MFRDFRReportsListView.as_view(), name='mfr-dfr-reports-list'),
    url(r'^mfr-dfr-reports/table/$', views.MFRDFRReportsListingTable.as_view(), name='mfr-dfr-reports-table'),
    url(r'^mfr-dfr-reports/upload/$', views.MFRDFRReportsCreateView.as_view(), name='mfr-dfr-reports-upload'),
    url(r'^mfr-dfr-reports/(?P<pk>\d+)/delete/$', views.MFRDFRReportsDeleteView.as_view(), name='mfr-dfr-reports-delete'),

    url(r'^dfr-processed-reports/$', views.DFRProcessedListView.as_view(), name='dfr-processed-reports-list'),
    url(r'^dfr-processed-reports/table/$', views.DFRProcessedListingTable.as_view(), name='dfr-processed-reports-table'),
    url(r'^dfr-processed-reports/(?P<pk>\d+)/download/$', views.dfr_processed_report_download, name='dfr-processed-reports-download'),

    url(r'^dfr-reports/$', views.DFRReportsListView.as_view(), name='dfr-reports-list'),
    url(r'^dfr-reports/table/$', views.DFRReportsListingTable.as_view(), name='dfr-reports-table'),
    url(r'^dfr-reports/(?P<pk>\d+)/delete/$', views.DFRReportsDeleteView.as_view(), name='dfr-reports-delete'),

    url(r'^mfr-reports/$', views.MFRReportsListView.as_view(), name='mfr-reports-list'),
    url(r'^mfr-reports/table/$', views.MFRReportsListingTable.as_view(), name='mfr-reports-table'),
    url(r'^mfr-reports/(?P<pk>\d+)/delete/$', views.MFRReportsDeleteView.as_view(), name='mfr-reports-delete'),

    url(r'^latency/wimax/$', views.WiMAX_Latency.as_view(), name='latency-wimax'),
    url(r'^latency/pmp/$', views.PMP_Latency.as_view(), name='latency-pmp'),
    url(r'^latency/all/$', views.ALL_Latency.as_view(), name='latency-all'),

    url(r'^packet_loss/wimax/$', views.WIMAX_Packet_Loss.as_view(), name='packet-loss-wimax'),
    url(r'^packet_loss/pmp/$', views.PMP_Packet_Loss.as_view(), name='packet-loss-pmp'),
    url(r'^packet_loss/all/$', views.ALL_Packet_Loss.as_view(), name='packet-loss-all'),

    url(r'^down/wimax/$', views.WIMAX_Down.as_view(), name='down-wimax'),
    url(r'^down/pmp/$', views.PMP_Down.as_view(), name='down-pmp'),
    url(r'^down/all/$', views.ALL_Down.as_view(), name='down-all'),

    url(r'^temperature-idu/wimax/$', views.WIMAX_Temperature_Idu.as_view(), name='temperatue-idu-wimax'),
    url(r'^temperature-acb/wimax/$', views.WIMAX_Temperature_Acb.as_view(), name='temperatue-acb-wimax'),
    url(r'^temperature-fan/wimax/$', views.WIMAX_Temperature_Fan.as_view(), name='temperatue-fan-wimax'),

    url(r'^cause-code/mfr/$', views.MFRCauseCodeView.as_view(), name='cause-code-mfr'),
    url(r'^processed/mfr/$', views.MFRProcesedView.as_view(), name='processed-mfr'),

    url(r'^sector-capacity/pmp/$', views.PMPSectorCapacity.as_view(), name='sector-capacity-pmp'),
    url(r'^sector-capacity/wimax/$', views.WiMAXSectorCapacity.as_view(), name='sector-capacity-wimax'),
)
