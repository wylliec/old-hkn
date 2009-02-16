from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^upload/$', 'resume.views.upload', name="resume-upload"),
    url(r'^missing/$', 'resume.views.missing', name="resume-missing"),
    url(r'^table-of-contents/$', 'resume.views.table_of_contents', name="resume-table-of-contents"),
    url(r'^table-of-contents-docs/$', 'resume.views.table_of_contents', {'docs_only' : True}, name="resume-list-docs"),
    url(r'^generate-book/$', 'resume.views.generate_book', name="resume-generate-book"),
    url(r'^delete-book/$', 'resume.views.delete_book', name="resume-delete-book"),
    url(r'^list-books/$', 'resume.views.list_books', name="resume-list-books"),
    url(r'^replace-doc/$', 'resume.views.replace_doc', name="resume-replace-doc"),
)
