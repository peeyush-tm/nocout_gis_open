from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.GISInventoryBulkImport.as_view(), name='gis_inventory_bulk_import'),
  url(r'^gis_inventory/$', views.GISInventoryBulkImport.as_view(), name='gis_inventory_bulk_import'),
  #url(r'^gis_inventory_bulk_processing/$', views.GISInventoryBulkProcessing.as_view(), name='gis_inventory_bulk_processing')
)