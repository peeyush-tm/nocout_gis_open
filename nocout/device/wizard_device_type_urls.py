from django.conf.urls import patterns, url

from device import views


urlpatterns = patterns('',
    url(r'^device-type/(?P<pk>\d+)/$', views.GisWizardDeviceTypeUpdateView.as_view(), name='wizard-device-type-update'),

    url(r'^device-type/(?P<dt_pk>\d+)/service/$', views.GisWizardServiceListView.as_view(), name='wizard-service-list'),
    url(r'^device-type/(?P<dt_pk>\d+)/service-table/$', views.GisWizardServiceListing.as_view(), name='wizard-service-list-table'),
    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<pk>\d+)/$', views.GisWizardServiceUpdateView.as_view(), name='wizard-service-update'),
    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<pk>\d+)/delete/$', views.wizard_service_delete, name='wizard-service-delete'),

    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<dts_pk>\d+)/data-source/$', views.GisWizardDataSourceListView.as_view(), name='wizard-data-source-list'),
    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<dts_pk>\d+)/data-source-table/$', views.GisWizardDataSourceListing.as_view(), name='wizard-data-source-list-table'),
    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<dts_pk>\d+)/data-source-table/(?P<pk>\d+)/delete/$', views.wizard_data_source_delete, name='wizard-data-source-delete'),
)
