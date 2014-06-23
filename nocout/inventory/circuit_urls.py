from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.CircuitList.as_view(), name='circuits_list'),
  url(r'^(?P<pk>\d+)$', views.CircuitDetail.as_view(), name='circuit_detail'),
  url(r'^new/$', views.CircuitCreate.as_view(), name='circuit_new'),
  url(r'^edit/(?P<pk>\d+)$', views.CircuitUpdate.as_view(), name='circuit_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.CircuitDelete.as_view(), name='circuit_delete'),
  url(r'^Circuitlistingtable/', views.CircuitListingTable.as_view(), name='CircuitListingTable'),
)