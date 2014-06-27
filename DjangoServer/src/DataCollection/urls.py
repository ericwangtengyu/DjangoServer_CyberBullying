from django.conf.urls import patterns, url
from DataCollection import views

urlpatterns = patterns('',
    url(r'^$', views.notUser, name='notUser'),
    url(r'^postandroid/$', views.postandroid, name='postandroid'),
    url(r'^gethelp/$', views.getHelp, name='Help'),
    url(r'^newtoken/$', views.newToken, name='newToken'),
    url(r'^withdraw/$', views.withdraw, name='withdraw'),
    url(r'^reportbullying/$', views.reportBulling, name='reportBulling'),
    url(r'^survey/$', views.survey, name='survey'), 
    url(r'^getfacetoken/$' , views.get_all_faceid , name= 'getfacetoken' ),
    url(r'^gettwittertoken/$' , views.get_all_twitter , name= 'gettwittertoken' ),
    url(r'^postfacebook/$' , views.facebook_post , name= 'facebookpost' ),
    url(r'^posttwitter/$' , views.twitter_post , name= 'twitter' ),
    url(r'^posttwitterseparate/$' , views.twitter_post_separate , name= 'twitterSeparatepost' ),
    url(r'^makeuser/$' , views.make_user , name= 'makeuser' ),
    url(r'^unifycollect/$' , views.unify_collect, name= 'unifycollect' ),
    url(r'^getalluser/$' , views.get_all_user, name= 'getalluser' ),
    url(r'^app/$', views.app , name='app'),
)
