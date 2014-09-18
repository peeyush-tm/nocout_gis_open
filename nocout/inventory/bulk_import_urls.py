from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.GISInventoryBulkImportList.as_view(), name='gis_inventory_bulk_import_list'),
  url(r'^gis_inventory/$', views.GISInventoryBulkImportView.as_view(), name='gis_inventory_bulk_import'),
  url(r'^gis_inventory_validator/$', views.GISInventoryBulkImportView.as_view(), name='gis_inventory_validator'),
    url(r'^gisinventorybulkimportlistingtable/', views.GISInventoryBulkImportListingTable.as_view(), name='GISInventoryBulkImportListingTable'),
  # url(r'^gis_inventory_bulk_processing/$', views.GISInventoryBulkProcessing.as_view(), name='gis_inventory_bulk_processing')
)