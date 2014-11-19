from django.conf.urls import patterns, url, include
from . import views


urlpatterns = patterns('',
    url(r'^$', 'inventory.views.inventory', name='inventory_home'),
    url(r'^new/',views.InventoryCreate.as_view(), name='InventoryCreate'),
    url(r'^(?P<pk>\d+)/edit/$', views.InventoryUpdate.as_view(), name='InvertoryUpdate'),
    url(r'^(?P<pk>\d+)/delete/$', views.InventoryDelete.as_view(), name='inventory_delete'),
    url(r'^inventorylist/',views.InventoryListing.as_view(), name='InventoryList'),
    url(r'^inventorylistingtable/',views.InventoryListingTable.as_view(), name='InventoryListingTable'),
    url(r'^inventory_details_wrt_organization/', views.inventory_details_wrt_organization, name='InventoryDetailWRTOrganization'),
    url(r'^export_excel_row_by_row/', views.ExcelWriterRowByRow.as_view(), name='ExcelWriterRowByRow'),
    url(r'^list/device/$', views.list_device, name='list-device'),
    url(r'^select/device/(?P<pk>\d+)/$', views.select_device, name='select-device'),
)
