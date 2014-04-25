from django.conf.urls import patterns, include, url
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'home.views.home'),
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
    url(r'^login/$', 'nocout.views.login'),
    url(r'^auth/$', 'nocout.views.auth_view'),
    url(r'^loggedin/$', 'nocout.views.loggedin'),
    url(r'^logout/$', 'nocout.views.logout'),
    url(r'^invalid/$', 'nocout.views.invalid_login'),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # Examples:
    # url(r'^$', 'nocout.views.home', name='home'),
    # url(r'^nocout/', include('nocout.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
