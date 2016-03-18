from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^get_auto_suggestions/(?P<search_by>\w+)/(?P<search_txt>[-_.:\w\x20]+)/$', views.getAutoSuggestion, name='get_auto_suggestion'),
  url(r'^get_search_data/(?P<search_by>\w+)/(?P<pk>\d+)/$', views.getSearchData, name='get_search_data')
)
