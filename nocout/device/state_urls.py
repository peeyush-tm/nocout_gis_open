from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.StateListing.as_view(), name='state_list'),
  url(r'^(?P<pk>\d+)/$', views.StateDetail.as_view(), name='state_detail'),
  url(r'^new/$', views.StateCreate.as_view(), name='state_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.StateUpdate.as_view(), name='state_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.StateDelete.as_view(), name='state_delete'),
  url(r'^statelistingtable/$', views.StateListingTable.as_view(), name='StateListingTable'),
)
