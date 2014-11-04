'''
Created on May 28, 2014

@author: maxclapp
'''
from django.conf.urls import patterns, url

from survey import views


urlpatterns = patterns('',
    url(r'^(?i)(?P<survey_id>\d+)/(?P<user_id>-?\d+)/$', views.survey,name='survey'),
   url(r'^(?i)(?P<survey_id>\d+)/(?P<user_id>-?\d+)/answer/$', views.answer,name='answer'),
   url(r'^(?i)(?P<survey_id>\d+)/results/$', views.results,name='results'),
   url(r'^(?i)(?P<survey_id>\d+)/(?P<user_id>-?\d+)/email/$', views.email,name='email'),
   url(r'^(?i)(?P<survey_id>\d+)/(?P<user_id>-?\d+)/sendemail/$', views.sendemail,name='sendemail'),
   url(r'^(?i)refresh/$', views.refresh,name='refresh'),
)
