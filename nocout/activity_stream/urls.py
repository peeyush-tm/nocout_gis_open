
from django.conf.urls import patterns, url
from activity_stream import views

urlpatterns = patterns('',
         url(r'^actions/$', views.ActionList.as_view(), name='actionlist'),
         url(r'^actionlistingtable/', views.ActionListingTable.as_view(), name='actionlistingtable'),
         url(r'^actions/log/$', views.log_user_action, name='log-user-action'),
         )


