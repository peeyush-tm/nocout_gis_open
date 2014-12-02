from django.conf.urls import patterns, url

from inventory import views


urlpatterns = patterns('',
    url(r'^base-station/$', views.GisWizardListView.as_view(), name='gis-wizard-base-station-list'),
    url(r'^base-station/table/$', views.GisWizardListingTable.as_view(), name='gis-wizard-base-station-list-table'),
    url(r'^ptp/$', views.GisWizardPTPListView.as_view(), name='gis-wizard-list-ptp'),
    url(r'^ptp/table/$', views.GisWizardPTPListingTable.as_view(), name='gis-wizard-ptp-list-table'),
    url(r'^sub-station/$', views.GisWizardSubStationListView.as_view(), name='gis-wizard-list-sub-station'),
    url(r'^sub-station/table/$', views.GisWizardSubStationListingTable.as_view(), name='gis-wizard-sub-station-list-table'),
    url(r'^base-station/select/$', views.gis_wizard_base_station_select, name='gis-wizard-base-station-select'),
    url(r'^base-station/new/$', views.GisWizardBaseStationCreateView.as_view(), name='gis-wizard-base-station-create'),
    url(r'^base-station/(?P<pk>\d+)/$', views.GisWizardBaseStationUpdateView.as_view(), name='gis-wizard-base-station-update'),
    url(r'^base-station/(?P<pk>\d+)/details/$', views.GisWizardBaseStationDetailView.as_view(), name='gis-wizard-base-station-detail'),

    url(r'^base-station/(?P<bs_pk>\d+)/backhaul/select/$', views.gis_wizard_backhaul_select, name='gis-wizard-backhaul-select'),
    url(r'^base-station/(?P<bs_pk>\d+)/backhaul/delete/$', views.gis_wizard_backhaul_delete, name='gis-wizard-backhaul-delete'),
    url(r'^base-station/(?P<bs_pk>\d+)/backhaul/new/$', views.GisWizardBackhaulCreateView.as_view(), name='gis-wizard-backhaul-create'),
    url(r'^base-station/(?P<bs_pk>\d+)/backhaul/(?P<pk>\d+)/$', views.GisWizardBackhaulUpdateView.as_view(), name='gis-wizard-backhaul-update'),
    url(r'^base-station/(?P<bs_pk>\d+)/backhaul/(?P<pk>\d+)/details/$', views.GisWizardBackhaulDetailView.as_view(), name='gis-wizard-backhaul-detail'),

    url(r'^base-station/(?P<bs_pk>\d+)/sectors/$', views.GisWizardSectorListView.as_view(), name='gis-wizard-sector-list'),
    url(r'^base-station/(?P<bs_pk>\d+)/sectors/(?P<pk>\d+)/delete/$', views.gis_wizard_sector_delete, name='gis-wizard-sector-delete'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[2|3|4])/sectors-table/$', views.GisWizardSectorListing.as_view(), name='gis-wizard-sector-list-table'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[2|3|4])/sector/select/$', views.gis_wizard_sector_select, name='gis-wizard-sector-select'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[2|3|4])/sector/new/$', views.GisWizardSectorCreateView.as_view(), name='gis-wizard-sector-create'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[2|3|4])/sector/(?P<pk>\d+)/$', views.GisWizardSectorUpdateView.as_view(), name='gis-wizard-sector-update'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[2|3|4])/sector/(?P<pk>\d+)/details/$', views.GisWizardSectorDetailView.as_view(), name='gis-wizard-sector-detail'),

    url(r'get-form/$', views.get_wizard_form, name='gis-wizard-form'),
    url(r'get-sub-station-antenna-formset/$', views.get_ptp_sub_station_antenna_wizard_form, name='gis-wizard-ptp-sub-station-antenna-form'),

    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-stations/$', views.GisWizardSectorSubStationListView.as_view(), name='gis-wizard-sub-station-list'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-stations-table/$', views.GisWizardSubStationListing.as_view(), name='gis-wizard-sub-station-list-table'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-station/select/$', views.gis_wizard_sub_station_select, name='gis-wizard-sub-station-select'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-station/(?P<pk>\d+)/delete/$', views.gis_wizard_sub_station_delete, name='gis-wizard-sub-station-delete'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-station/new/$', views.GisWizardSubStationCreateView.as_view(), name='gis-wizard-sub-station-create'),
    url(r'^base-station/(?P<bs_pk>\d+)/technology/(?P<selected_technology>[3|4])/sector/(?P<sector_pk>\d+)/sub-station/(?P<pk>\d+)/$', views.GisWizardSubStationUpdateView.as_view(), name='gis-wizard-sub-station-update'),
)
