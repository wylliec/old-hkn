from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Example:
	# (r'^candportal/', include('candportal.foo.urls')),
	
	# View URL patterns go here:
		#(r'^$', 'hkn.info.list.list_all'),
		(r'^list/(?P<person_class>.*)/$', 'hkn.info.list.list_people'),
		(r'^list/$', 'hkn.info.list.list_people', {"person_class" : "all"}),
		(r'^quiz/(?P<person_class>.*)/$', 'hkn.info.quiz.quiz'),
		(r'^details/(?P<id>\d+)/$', 'hkn.info.views.details'),
		(r'^pictures/(?P<id>\d+)/$', 'hkn.info.views.pictures')	,
		(r'^find_person/$', 'hkn.info.find.find_person'),
		(r'^list_people_ajax/$', 'hkn.info.list.list_people_ajax'),
		(r'^elect/$', 'hkn.info.elect.elect'),

		#(r'^?P<committee>\w/$', 'hkn.info.list.list_committee'),
	)					    
