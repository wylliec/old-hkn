from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^new/$', 'hkn.event.views.new'),
		(r'^list/$', 'hkn.event.views.list'),
		(r'^calendar/$', 'hkn.event.views.calendar'),
		(r'^edit/(?P<event_id>.*)/$', 'hkn.event.views.edit'),
		(r'^delete/(?P<event_id>.*)/$', 'hkn.event.views.delete'),
		(r'^rsvp/list/(?P<event_id>.*)/$', 'hkn.event.rsvp.list'),
		(r'^rsvp/mine/$', 'hkn.event.rsvp.my_rsvps'),
		(r'^rsvp/delete/(?P<event_id>.*)/$', 'hkn.event.rsvp.delete'),
		(r'^rsvp/view/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.view'),
		(r'^rsvp_form/$', 'hkn.event.rsvp.rsvp_form'),
		(r'^rsvp/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp'),
	)					    
