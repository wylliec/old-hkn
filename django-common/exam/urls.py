from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Example:

	# main page
	url(r'^$', 'exam.views.browse'),
	url(r'^view/(?P<exam_id>\d+)/$', 'exam.views.view', name="exam-view"),    
	#url(r'^submit/$', 'exam.submit.submit', name="exam-submit"),
	url(r'^browse/(?P<department_abbr>.*)/$', 'exam.views.browse_department', name="exam-browse-department"),
	url(r'^browse/$', 'exam.views.browse', name="exam-browse"),
	url(r'^list/$', 'exam.list.list_exams', name="exam-list"),
	url(r'^exam_autocomplete/$', 'exam.views.exam_autocomplete', name='exam-autocomplete'),
	#url(r'^list_ajax/$', 'exam.list.list_exams_ajax', name="exam-list-ajax"),        
	#url(r'^list/(?P<course>.*)/(?P<exam_type>.*)/$', 'exam.views.list_exams', name="exam-list-course-type"),    
	#url(r'^list/(?P<course>.*)/$', 'exam.views.list_exams', name="exam-list-course"),
	#url(r'^list/$', 'exam.views.list_exams', name="exam-list"),
)
