from django.conf.urls import patterns, url
from DataCollection import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^postandroid/$', views.postandroid, name='postandroid'),
    url(r'^getfacetoken/$' , views.get_all_faceid , name= 'getfacetoken' ),
    url(r'^gettwittertoken/$' , views.get_all_twitter , name= 'gettwittertoken' ),
    url(r'^postfacebook/$' , views.facebook_post , name= 'facebookpost' ),
    url(r'^posttwitter/$' , views.twitter_post , name= 'twitter' ),
    url(r'^posttwitterseparate/$' , views.twitter_post_separate , name= 'twitterSeparatepost' ),
    url(r'^makeuser/$' , views.make_user , name= 'makeuser' ),
)
