from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DjangoServer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^DataCollection/', include('DataCollection.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^survey/',include('survey.urls',namespace="survey")),
)
