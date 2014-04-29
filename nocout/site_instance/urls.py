from django.conf.urls import patterns, url

from site_instance import views

urlpatterns = patterns('',
    url(r'^$', views.SiteInstanceList.as_view(), name='site_instance_list'),
    url(r'^(?P<pk>\d+)$', views.SiteInstanceDetail.as_view(), name='site_instance_detail'),
    url(r'^new/$', views.SiteInstanceCreate.as_view(), name='site_instance_new'),
    url(r'^edit/(?P<pk>\d+)$', views.SiteInstanceUpdate.as_view(), name='site_instance_edit'),
    url(r'^delete/(?P<pk>\d+)$', views.SiteInstanceDelete.as_view(), name='site_instance_delete'),
)