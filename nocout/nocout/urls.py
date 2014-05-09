from django.conf import settings
from django.conf.urls import patterns, include, url
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^home/', 'home.views.home'),
    url(r'^user/', include('user_profile.urls')),
    url(r'^ug/', include('user_group.urls')),
    url(r'^device/', include('device.urls')),
    url(r'^dg/', include('device_group.urls')),
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


