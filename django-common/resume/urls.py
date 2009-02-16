from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^upload/$', 'resume.views.upload', name="resume-upload"),
    url(r'^missing/$', 'resume.views.missing', name="resume-missing"),
    url(r'^table-of-contents/$', 'resume.views.table_of_contents', name="resume-table-of-contents"),
)
