from django.conf.urls import patterns, url
from downloader import views

urlpatterns = patterns('',
                       url(r'^$', views.DownloaderCompleteHeaders.as_view(),
                           name='DownloaderCompleteHeaders'),
                       url(r'^datatable/$', views.DataTableDownloader.as_view()),
                       url(r'^list/', views.DownloaderHeaders.as_view(),
                           name='Downloader'),
                       url(r'^downloaderlistingtable/', views.DownloaderListing.as_view(),
                           name='DownloaderListing'),
                       url(r'^delete/(?P<pk>\d+)$', views.DownloaderDelete.as_view(), name='download_delete'),
                       url(r'^downloadercompletelistingtable/', views.DownloaderCompleteListing.as_view(),
                           name='DownloaderCompleteListing'),
                       url(r'^delete/(?P<pk>\d+)$', views.DownloaderDelete.as_view(), name='download_delete'),
)
