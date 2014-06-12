from django.conf.urls import patterns, url
from scheduling_management import views


urlpatterns = patterns('',
    url(r'^$', views.get_scheduler)
)