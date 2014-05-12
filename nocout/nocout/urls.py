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
    url(r'^home/', 'home.views.home'),
    url(r'^user/', include('user_profile.urls')),
    url(r'^ug/', include('user_group.urls')),
    url(r'^device/', include('device.urls')),
    url(r'^dg/', include('device_group.urls')),
    url(r'^command/', include('command.urls')),
    url(r'^service/', include('service.urls')),
    url(r'^sp/', include('service.para_urls')),
    url(r'^site/', include('site_instance.urls')),
    url(r'^device_fields/', include('device.device_extra_fields_urls')),
    url(r'^technology/', include('device.device_technology_urls')),
    url(r'^vendor/', include('device.device_vendor_urls')),
    url(r'^model/', include('device.device_model_urls')),
    url(r'^type/', include('device.device_type_urls')),
    url(r'^login/$', 'nocout.views.login'),
    url(r'^auth/$', 'nocout.views.auth_view'),
    url(r'^loggedin/$', 'nocout.views.loggedin'),
    url(r'^logout/$', 'nocout.views.logout'),
    url(r'^invalid/$', 'nocout.views.invalid_login'),
    url(r'^site/', include('site_instance.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'session_security/', include('session_security.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
