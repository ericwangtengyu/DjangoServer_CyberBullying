'''
Created on May 28, 2014

@author: maxclapp
'''
from django.conf.urls import patterns, url

from survey import views


urlpatterns = patterns('',
    url(r'^(?P<survey_id>\d+)/(?P<user_id>\d+)/$', views.survey,name='survey'),
   url(r'^(?P<survey_id>\d+)/(?P<user_id>\d+)/answer/$', views.answer,name='answer'),
   url(r'^(?P<survey_id>\d+)/results/$', views.results,name='results'),
)
