from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^list/(?P<category>.*)/$', 'hkn.event.list.list_events'),
        (r'^list/$', 'hkn.event.list.list_events', {"category" : "future"}),
        (r'^list_ajax/$', 'hkn.event.list.list_events_ajax'),
        

        (r'^calendar/$', 'hkn.event.event.calendar'),
        url(r'^view/(?P<event_id>.*)/$', 'hkn.event.event.view', name="event-view"),
        url(r'^infobox/(?P<event_id>.*)/$', 'hkn.event.event.infobox', name="event-infobox"),

        (r'^rsvp/', include('hkn.event.rsvp.urls')),
    )					    
