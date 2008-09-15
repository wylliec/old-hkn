from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^upload/$', 'resume.views.upload', name="resume-upload"),
)
