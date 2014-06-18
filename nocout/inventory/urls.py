from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'inventory.views.inventory', name='inventory_home'),
    url(r'^antenna/', include('inventory.antenna_urls')),
)