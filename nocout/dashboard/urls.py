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

    url(r'^rf-dashbaord/main/$', views.MainDashboard.as_view(), name='rf-main-dashbaord'),

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

    url(r'^latency/wimax/$', views.DashboardDeviceStatus.as_view(), name='latency-wimax'),
    url(r'^latency/pmp/$', views.DashboardDeviceStatus.as_view(), name='latency-pmp'),
    url(r'^latency/all/$', views.DashboardDeviceStatus.as_view(), name='latency-all'),

    url(r'^packet_loss/wimax/$', views.DashboardDeviceStatus.as_view(), name='packet-loss-wimax'),
    url(r'^packet_loss/pmp/$', views.DashboardDeviceStatus.as_view(), name='packet-loss-pmp'),
    url(r'^packet_loss/all/$', views.DashboardDeviceStatus.as_view(), name='packet-loss-all'),

    url(r'^down/wimax/$', views.DashboardDeviceStatus.as_view(), name='down-wimax'),
    url(r'^down/pmp/$', views.DashboardDeviceStatus.as_view(), name='down-pmp'),
    url(r'^down/all/$', views.DashboardDeviceStatus.as_view(), name='down-all'),

    url(r'^temperature-idu/wimax/$', views.DashboardDeviceStatus.as_view(), name='temperatue-idu-wimax'),
    url(r'^temperature-acb/wimax/$', views.DashboardDeviceStatus.as_view(), name='temperatue-acb-wimax'),
    url(r'^temperature-fan/wimax/$', views.DashboardDeviceStatus.as_view(), name='temperatue-fan-wimax'),

    url(r'^cause-code/mfr/$', views.MFRCauseCodeView.as_view(), name='cause-code-mfr'),
    url(r'^processed/mfr/$', views.MFRProcesedView.as_view(), name='processed-mfr'),

    url(r'^sector-capacity/pmp/$', views.PMPSectorCapacity.as_view(), name='sector-capacity-pmp'),
    url(r'^sector-capacity/wimax/$', views.WiMAXSectorCapacity.as_view(), name='sector-capacity-wimax'),

    url(r'^backhaul-capacity/pmp/$', views.PMPBackhaulCapacity.as_view(), name='backhaul-capacity-pmp'),
    url(r'^backhaul-capacity/wimax/$', views.WiMAXBackhaulCapacity.as_view(), name='backhaul-capacity-wimax'),
    url(r'^backhaul-capacity/tclpop/$', views.TCLPOPBackhaulCapacity.as_view(), name='backhaul-capacity-tclpop'),


    url(r'^sales-opportunity/pmp/$', views.PMPSalesOpportunity.as_view(), name='sales-opportunity-pmp'),
    url(r'^sales-opportunity/wimax/$', views.WiMAXSalesOpportunity.as_view(), name='sales-opportunity-wimax'),

    url(r'^trend-monthly-sector/pmp/$', views.MonthlyTrendSectorPMP.as_view(), name = 'trend-monthly-sector-pmp' ),
    url(r'^trend-monthly-sector/wimax/$', views.MonthlyTrendSectorWIMAX.as_view(), name = 'trend-monthly-sector-wimax' ),

    url(r'^trend-monthly-sales/pmp/$', views.MonthlyTrendSalesPMP.as_view(), name = 'trend-monthly-sales-pmp' ),
    url(r'^trend-monthly-sales/wimax/$', views.MonthlyTrendSalesWIMAX.as_view(), name = 'trend-monthly-sales-wimax' ),

    url(r'^trend-monthly-down/all/$', views.MonthlyTrendDashboardDeviceStatus.as_view(), name = 'trend-monthly-down-all' ),
    url(r'^trend-monthly-latency/all/$', views.MonthlyTrendDashboardDeviceStatus.as_view(), name = 'trend-monthly-latency-all' ),
    url(r'^trend-monthly-packet_loss/all/$', views.MonthlyTrendDashboardDeviceStatus.as_view(), name = 'trend-monthly-packet-loss-all' ),
    url(r'^trend-monthly-temperature-idu/wimax/$', views.MonthlyTrendDashboardDeviceStatus.as_view(), name = 'trend-monthly-temperature-idu-wimax' ),

    url(r'^trend-monthly-backhaul/pmp/$', views.MonthlyTrendBackhaulPMP.as_view(), name = 'trend-monthly-backhaul-pmp' ),
    url(r'^trend-monthly-backhaul/wimax/$', views.MonthlyTrendBackhaulWiMAX.as_view(), name = 'trend-monthly-backhaul-wimax' ),
    url(r'^trend-monthly-backhaul/tclpop/$', views.MonthlyTrendBackhaulTCLPOP.as_view(), name = 'trend-monthly-backhaul-tclpop' ),
)
