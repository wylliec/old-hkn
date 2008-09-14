from django.conf.urls.defaults import *
from resume import views

urlpatterns = patterns('',
    url(r'^upload/$', views.upload, name="resume-upload"),
)
