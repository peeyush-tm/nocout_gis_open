from django.conf.urls import patterns, url

from site_instance import views

urlpatterns = patterns('',
  url(r'^$', views.SiteinstanceList.as_view(), name='site_list'),
  url(r'^(?P<pk>\d+)$', views.SiteinstanceDetail.as_view(), name='site_detail'),
  url(r'^new/$', views.SiteinstanceCreate.as_view(), name='site_new'),
  url(r'^edit/(?P<pk>\d+)$', views.SiteinstanceUpdate.as_view(), name='site_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.SiteInstanceDelete.as_view(), name='site_delete'),
)