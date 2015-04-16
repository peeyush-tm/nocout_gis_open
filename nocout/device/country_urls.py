from django.conf.urls import patterns, url
from device import views

urlpatterns = patterns('',
  url(r'^$', views.CountryListing.as_view(), name='country_list'),
  url(r'^(?P<pk>\d+)/$', views.CountryDetail.as_view(), name='country_detail'),
  url(r'^new/$', views.CountryCreate.as_view(), name='country_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.CountryUpdate.as_view(), name='country_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.CountryDelete.as_view(), name='country_delete'),
  url(r'^countrylistingtable/$', views.CountryListingTable.as_view(), name='CountryListingTable'),
)
