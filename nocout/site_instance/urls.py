from django.conf.urls import patterns, url
from site_instance import views

urlpatterns = patterns('',
    url(r'^$', views.SiteInstanceList.as_view(), name='site_instance_list'),
    url(r'^(?P<pk>\d+)/$', views.SiteInstanceDetail.as_view(), name='site_instance_detail'),
    url(r'^new/$', views.SiteInstanceCreate.as_view(), name='site_instance_new'),
    url(r'^(?P<pk>\d+)/edit/$', views.SiteInstanceUpdate.as_view(), name='site_instance_edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.SiteInstanceDelete.as_view(), name='site_instance_deletes'),
    url(r'^SiteInstanceListingTable/', views.SiteInstanceListingTable.as_view(), name='SiteInstanceListingTable'),
)
