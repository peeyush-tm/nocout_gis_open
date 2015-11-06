from django.conf.urls import patterns, url, include
from alarm_escalation import views


urlpatterns = patterns('',
                       #url(r'^$', views.EscalationList.as_view(), name='escalation_list'),
                       #url(r'^new/', views.AlarmEscalationCreate.as_view(), name='escalation_create'),
                       #url(r'^(?P<pk>\d+)/edit/$', views.AlarmEscalationUpdate.as_view(), name='escalation_update'),
                       #url(r'^(?P<pk>\d+)/delete/$', views.AlarmEscalationDelete.as_view(), name='escalation_delete'),
                       #url(r'^escalationlistingtable/', views.EscalationListingTable.as_view(),
                           #name='EscalationListingTable'),
                       url(r'^level/$', views.LevelList.as_view(), name='level_list'),
                       url(r'^level/new/', views.LevelCreate.as_view(), name='level_create'),
                       url(r'^level/(?P<pk>\d+)/edit/$', views.LevelUpdate.as_view(), name='level_update'),
                       url(r'^level/(?P<pk>\d+)/delete/$', views.LevelDelete.as_view(), name='level_delete'),
                       url(r'^levellistingtable/', views.LevelListingTable.as_view(),
                           name='LevelListingTable'),
                       url(r'^email/$', views.EmailSender.as_view(), name='send_email')

)
