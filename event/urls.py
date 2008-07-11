from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^list/(?P<category>.*)/$', 'hkn.event.list.list_events'),
        (r'^list/$', 'hkn.event.list.list_events', {"category" : "future"}),
        (r'^list_ajax/$', 'hkn.event.list.list_events_ajax'),
        

        (r'^calendar/$', 'hkn.event.event.calendar'),
        (r'^view/(?P<event_id>.*)/$', 'hkn.event.event.view'),

        (r'^rsvp/', include('hkn.event.rsvp.urls')),
    )					    
