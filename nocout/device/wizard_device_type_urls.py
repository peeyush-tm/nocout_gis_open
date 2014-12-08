from django.conf.urls import patterns, url

from device import views


urlpatterns = patterns('',
    url(r'^device-type/$', views.GisWizardDeviceTypeCreateView.as_view(), name='wizard-device-type-create'),
    url(r'^device-type/(?P<pk>\d+)/$', views.GisWizardDeviceTypeUpdateView.as_view(), name='wizard-device-type-update'),

    url(r'^device-type/(?P<dt_pk>\d+)/service/$', views.GisWizardServiceListView.as_view(), name='wizard-service-list'),
    url(r'^device-type/(?P<dt_pk>\d+)/service-table/$', views.GisWizardServiceListing.as_view(), name='wizard-service-list-table'),
    url(r'^device-type/(?P<dt_pk>\d+)/service/(?P<pk>\d+)/$', views.GisWizardServiceUpdateView.as_view(), name='wizard-service-update'),

)
