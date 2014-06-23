from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
# Include dajaxice ajax module
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',RedirectView.as_view(url='login/')),
    url(r'^home/', 'home.views.home', name='home'),
    url(r'^user/', include('user_profile.urls')),
    url(r'^user_group/', include('user_group.urls')),
    url(r'^device/', include('device.urls')),
    url(r'^device_group/', include('device_group.urls')),
    url(r'^organization/', include('organization.urls')),
    url(r'^command/', include('command.urls')),
    url(r'^service/', include('service.urls')),
    url(r'^service_parameter/', include('service.para_urls')),
    url(r'^machine/', include('machine.urls')),
    url(r'^site/', include('site_instance.urls')),
    url(r'^device_fields/', include('device.device_extra_fields_urls')),
    url(r'^technology/', include('device.device_technology_urls')),
    url(r'^vendor/', include('device.device_vendor_urls')),
    url(r'^model/', include('device.device_model_urls')),
    url(r'^type/', include('device.device_type_urls')),
    url(r'^antenna/', include('inventory.antenna_urls')),
    url(r'^base_station/', include('inventory.base_station_urls')),
    url(r'^backhaul/', include('inventory.backhaul_urls')),
    url(r'^sector/', include('inventory.sector_urls')),
    url(r'^customer/', include('inventory.customer_urls')),
    url(r'^sub_station/', include('inventory.sub_station_urls')),
    url(r'^circuit/', include('inventory.circuit_urls')),
    url(r'^login/$', 'nocout.views.login'),
    url(r'^auth/$', 'nocout.views.auth_view'),
    url(r'^logout/$', 'nocout.views.logout'),
    url(r'^site/', include('site_instance.urls')),
    url(r'^network_maps/', include('devicevisualization.urls')),
    url(r'^gis/', include('sitesearch.urls')),
    url(r'^alert_center/', include('alert_center.urls')),
    url(r'^capacity_management/', include('capacity_management.urls')),
    url(r'^performance/', include('performance.urls')),
    url(r'^scheduling/', include('scheduling_management.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'session_security/', include('session_security.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logs/', include('activity_stream.urls')),
    url(r'^sm/', include('session_management.urls'))
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
