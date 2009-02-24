from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^list/(?P<category>.*)/$', 'hkn.event.list.list_events', name="event-list-category"),
        url(r'^list/$', 'hkn.event.list.list_events', {"category" : "future"}, name="event-list"),
        
        url(r'^feed/$', 'hkn.event.feed.feed', name="event-feed"),        

        url(r'^calendar/$', 'hkn.event.event.calendar', name="event-calendar"),
        url(r'^view/(?P<event_id>.*)/$', 'hkn.event.event.view', name="event-view"),
        url(r'^infobox/(?P<event_id>.*)/$', 'hkn.event.event.infobox', name="event-infobox"),
        url(r'^event_autocomplete/$', 'hkn.event.event.event_autocomplete', {'manager' : 'current_semester'}, name='event-autocomplete'),

        (r'^rsvp/', include('hkn.event.rsvp.urls')),
    )					    
