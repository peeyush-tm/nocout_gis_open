from django.conf.urls import patterns, url, include
from . import views


urlpatterns = patterns('',
                       url(r'^export_excel_row_by_row/', views.ExcelWriterRowByRow.as_view(),
                           name='ExcelWriterRowByRow'),
                       url(r'^export_selected_bs_inventory/', views.DownloadSelectedBSInventory.as_view(),
                           name='DownloadSelectedBSInventory'),
)
