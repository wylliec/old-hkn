from django.conf.urls.defaults import *
from settings import SERVER_ROOT

urlpatterns = patterns('',
    # Example:

    # main page
    (r'^$', 'exam.views.browse'),
    url(r'^submit/$', 'exam.exam.submit', name="exam-submit"),
    url(r'^browse/(?P<department_abbr>.*)/$', 'exam.views.browse_department', name="exam-browse-department"),
    url(r'^browse/$', 'exam.views.browse', name="exam-browse"),
    url(r'^list/(?P<course>.*)/(?P<exam_type>.*)/$', 'exam.list.list_exams', name="exam-list-course-type"),    
    url(r'^list/(?P<course>.*)/$', 'exam.list.list_exams', name="exam-list-course"),
    url(r'^list/$', 'exam.list.list_exams', name="exam-list"),
    url(r'^list_ajax/$', 'exam.list.list_exams_ajax', name="exam-list-ajax"),        
)
