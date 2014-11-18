from django.conf.urls import patterns, url
from DataCollection import views
from DataCollection import new_user_views
from DataCollection import data_post_views

urlpatterns = patterns('',
	url(r'^$', views.mainPage, name='mainPage'),
	url(r'^(?i)postandroid/$',          data_post_views.postandroid, name='postandroid'),
	url(r'^(?i)instructions/$',         views.instructions, name='insturctions'),
	url(r'^(?i)gethelp/$',              views.getHelp, name='gethelp'),
	url(r'^(?i)newtoken/$',             views.newToken, name='newToken'),
	url(r'^(?i)withdraw/$',             views.withdraw, name='withdraw'),
	url(r'^(?i)survey/$',               views.survey, name='survey'), 
	url(r'^(?i)getfacetoken/$' ,        views.get_all_faceid , name= 'getfacetoken' ),
	url(r'^(?i)gettwittertoken/$' ,     views.get_all_twitter , name= 'gettwittertoken' ),
	url(r'^(?i)postfacebook/$' ,        data_post_views.facebook_post , name= 'facebookpost' ),
	url(r'^(?i)posttwitter/$' ,         data_post_views.twitter_post , name= 'twitter' ),
	url(r'^(?i)posttwitterseparate/$' , data_post_views.twitter_post_separate , name= 'twitterSeparatepost' ),
	url(r'^(?i)makeuser/$' ,            new_user_views.make_user , name= 'makeuser' ),
	url(r'^(?i)unifycollect/$' ,        views.unify_collect, name= 'unifycollect' ),
	url(r'^(?i)getalluser/$' ,          views.get_all_user, name= 'getalluser' ),
	url(r'^(?i)app/$',                  views.app , name='app'),
	url(r'^(?i)facebookbackend/$' ,     new_user_views.facebookLoginBackend, name= "facebookbackend"),
	url(r'^(?i)twittercallback/$' ,     new_user_views.twitterCallBack),
	url(r'^(?i)emailbackend/$' ,        new_user_views.emailBackend, name= "emailbackend"),
	url(r'^(?i)login/$' ,               new_user_views.emailLogin),
	url(r'^(?i)twitterlogin/$',         new_user_views.twitterLogin, name= "twitterlogin"),
	url(r'^(?i)notwitter/$',            new_user_views.noTwitter, name= "notwitter"),
	url(r'^(?i)resources/$',            views.resources, name='resources'),
	url(r'^(?i)surveylogin/$',          views.surveyLogin, name= "surveylogin"),
	url(r'^(?i)startlogin/$',           views.startLogin, name= "startlogin"),
	url(r'^(?i)sendoutsurvey/$',        views.sendOutSurvey, name= "sendoutsurvey"),
	url(r'^(?i)sendemail/$',            views.sendEmail, name= "sendemail"),
	url(r'^(?i)generateUserDeltas/$',   views.generateUserDeltas, name = "generateUserDeltas"),
	url(r'^(?i)iphoneback/$',           new_user_views.iphoneBackEnd, name= "iphoneBackEnd"),
	url(r'^(?i)iphoneloginbackend/$',   new_user_views.iphoneLoginBackend, name= "iphoneloginbackend"),
	url(r'^(?i)faculty/$',              views.faculty, name="faculty"),
	url(r'^(?i)text/$',                 views.text, name="text"),
	url(r'^(?i)textbackend/$',          views.textBackend, name="textbackend"),
)
