from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DjangoServer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^(?i)DataCollection/', include('DataCollection.urls',namespace="DataCollection")),
    url(r'^(?i)admin/', include(admin.site.urls)),
    url(r'^(?i)survey/',include('survey.urls',namespace="survey")),
    url(r'^(?i)cyber-bullying/', include('DataCollection.urls',namespace="cyber-bullying")),
)
