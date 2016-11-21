from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^get_sms/$', views.GetSms.as_view(), name='get_sms'),
  # url(r'^get_search_data/(?P<search_by>\w+)/(?P<pk>\d+)/$', views.getSearchData, name='get_search_data')
)