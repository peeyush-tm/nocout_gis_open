from django.conf.urls import patterns, url
from inventory import views
from django.contrib.auth.decorators import permission_required


urlpatterns = patterns('',
                       url(r'^$', views.DownloadSelectedBSInventoryList.as_view(), name='gis_selected_bs_inventories_list'),
                       url(r'^gis_selected_bs_inventories/$', permission_required('is_superuser')(views.DownloadSelectedBSInventory.as_view()),
                           name='gis_selected_bs_inventories'),
                       url(r'^gis_selected_bs_inventorieslistingtable/', views.DownloadSelectedBSInventoryListingTable.as_view(),
                           name='DownloadSelectedBSInventoryListingTable'),
                       url(r'^(?P<pk>\d+)/delete/$', views.DownloadSelectedBSInventoryDelete.as_view(),
                           name='gis_selected_bs_inventories_delete'),
                       url(r'^(?P<pk>\d+)/edit/$', views.DownloadSelectedBSInventoryUpdate.as_view(),
                           name='gis_selected_bs_inventories_edit')
)
