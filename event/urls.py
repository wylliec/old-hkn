from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^list/(?P<category>.*)/$', 'hkn.event.list.list_events'),
		(r'^list/$', 'hkn.event.list.list_events', {"category" : "future"}),
		(r'^list_events_ajax/$', 'hkn.event.list.list_events_ajax'),
		
		(r'^calendar/$', 'hkn.event.event.calendar'),
		(r'^edit/(?P<event_id>.*)/$', 'hkn.event.event.edit'),
		(r'^delete/(?P<event_id>.*)/$', 'hkn.event.event.delete'),
		(r'^view/(?P<event_id>.*)/$', 'hkn.event.event.view'),
		(r'^new/$', 'hkn.event.event.new'),		
		
		(r'^rsvp/', include('hkn.event.rsvp.urls')),
	)					    
