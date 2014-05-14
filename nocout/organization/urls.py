from django.conf.urls import patterns, url
from organization import views

urlpatterns = patterns('',
    url(r'^$', views.OrganizationList.as_view(), name='organization_list'),
    url(r'^(?P<pk>\d+)$', views.OrganizationDetail.as_view(), name='organization_detail'),
    url(r'^new/$', views.OrganizationCreate.as_view(), name='organization_new'),
    url(r'^edit/(?P<pk>\d+)$', views.OrganizationUpdate.as_view(), name='organization_edit'),
    url(r'^delete/(?P<pk>\d+)$', views.OrganizationDelete.as_view(), name='organization_delete'),
)