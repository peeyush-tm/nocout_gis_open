from django.conf.urls import patterns, url
from scheduling_management import views


urlpatterns = patterns('',
    # url(r'^$', views.get_scheduler, name='scheduler'),
    url(r'^$', views.EventList.as_view(), name='event_list'),
    url(r'^EventListingTable/', views.EventListingTable.as_view(), name='EventListingTable'),
    url(r'^new/$', views.EventCreate.as_view(), name='event_new'),
    url(r'^(?P<pk>\d+)/edit/$', views.EventUpdate.as_view(), name='event_edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event_delete'),
    url(r'^month/$', views.get_month_event_list, name='monthly-event'),
)
