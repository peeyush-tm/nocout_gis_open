
from django.conf.urls import patterns, url
from activity_stream import views

urlpatterns = patterns('',
         url(r'^actions/$', views.ActionList.as_view(), name='actionlist'),
         url(r'^actionlistingtable/', views.ActionListingTable.as_view(), name='actionlistingtable'),
         )


