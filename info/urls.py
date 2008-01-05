from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Example:
	# (r'^candportal/', include('candportal.foo.urls')),
	
	# View URL patterns go here:
		#(r'^$', 'hkn.info.list.list_all'),
		(r'^view/(?P<person_id>\d+)/$', 'hkn.info.person.view'),
		(r'^pictures/(?P<person_id>\d+)/$', 'hkn.info.person.pictures')	,		
		
		(r'^list/(?P<category>.*)/$', 'hkn.info.list.list_people'),
		(r'^list/$', 'hkn.info.list.list_people', {"category" : "all"}),
		(r'^list_people_ajax/$', 'hkn.info.list.list_people_ajax'),
		(r'^quiz/(?P<category>.*)/$', 'hkn.info.quiz.quiz'),

		(r'^find_person/$', 'hkn.info.find.find_person'),
		(r'^elect/$', 'hkn.info.elect.elect'),
		(r'^revolt/$', 'hkn.info.elect.revolt'),		
		

		#(r'^?P<committee>\w/$', 'hkn.info.list.list_committee'),
	)					    
