from django.conf.urls import patterns, url
from inventory import views
from django.contrib.auth.decorators import permission_required


urlpatterns = patterns('',
                       url(r'^$', views.GISInventoryBulkImportList.as_view(), name='gis_inventory_bulk_import_list'),
                       url(r'^gis_inventory/$', permission_required('is_superuser')(views.GISInventoryBulkImportView.as_view()),
                           name='gis_inventory_bulk_import'),
                       url(r'^gis_inventory_validator/$', views.GISInventoryBulkImportView.as_view(),
                           name='gis_inventory_validator'),
                       url(r'^gisinventorybulkimportlistingtable/', views.GISInventoryBulkImportListingTable.as_view(),
                           name='GISInventoryBulkImportListingTable'),
                       url(r'^delete/(?P<pk>\d+)$', views.GISInventoryBulkImportDelete.as_view(),
                           name='gis_inventory_bulk_import_delete'),
                       url(r'^edit/(?P<pk>\d+)$', views.GISInventoryBulkImportUpdate.as_view(),
                           name='gis_inventory_bulk_import_edit'),
                       url(r'^bulk_upload_valid_data/(?P<sheettype>.+)/(?P<id>\d+)/(?P<sheetname>.+)/$', views.BulkUploadValidData.as_view(),
                           name='BulkUploadValidData'),
)