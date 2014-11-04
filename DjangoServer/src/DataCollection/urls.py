from django.conf.urls import patterns, url
from DataCollection import views

urlpatterns = patterns('',
	url(r'^$', views.mainPage, name='mainPage'),
	url(r'^(?i)postandroid/$', views.postandroid, name='postandroid'),
	url(r'^(?i)instructions/$', views.instructions, name='insturctions'),
	url(r'^(?i)gethelp/$', views.getHelp, name='Help'),
	url(r'^(?i)newtoken/$', views.newToken, name='newToken'),
	url(r'^(?i)withdraw/$', views.withdraw, name='withdraw'),
	url(r'^(?i)survey/$', views.survey, name='survey'), 
	url(r'^(?i)getfacetoken/$' , views.get_all_faceid , name= 'getfacetoken' ),
	url(r'^(?i)gettwittertoken/$' , views.get_all_twitter , name= 'gettwittertoken' ),
	url(r'^(?i)postfacebook/$' , views.facebook_post , name= 'facebookpost' ),
	url(r'^(?i)posttwitter/$' , views.twitter_post , name= 'twitter' ),
	url(r'^(?i)posttwitterseparate/$' , views.twitter_post_separate , name= 'twitterSeparatepost' ),
	url(r'^(?i)makeuser/$' , views.make_user , name= 'makeuser' ),
	url(r'^(?i)unifycollect/$' , views.unify_collect, name= 'unifycollect' ),
	url(r'^(?i)getalluser/$' , views.get_all_user, name= 'getalluser' ),
	url(r'^(?i)app/$', views.app , name='app'),
	url(r'^(?i)facebookbackend/$' , views.facebookLoginBackend, name= "facebookbackend"),
	url(r'^(?i)twittercallback/$' , views.twitterCallBack),
	url(r'^(?i)emailbackend/$' , views.emailBackend, name= "emailbackend"),
	url(r'^(?i)login/$' , views.emailLogin),
	url(r'^(?i)twitterlogin/$', views.twitterLogin, name= "twitterlogin"),
	url(r'^(?i)notwitter/$', views.noTwitter, name= "notwitter"),
	url(r'^(?i)resources/$', views.resources, name='resources'),
	url(r'^(?i)surveylogin/$', views.surveyLogin, name= "surveylogin"),
	url(r'^(?i)startlogin/$', views.startLogin, name= "startlogin"),
	url(r'^(?i)sendsurvey/$', views.sendOutSurvey, name= "sendsurvey"),
	url(r'^(?i)generateUserDeltas/$', views.generateUserDeltas, name = "generateUserDeltas")

)
