from django.conf.urls.defaults import *

urlpatterns = patterns('',
        
        # standard new, edit, delete views
        (r'^delete/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.rsvp.delete'),
        (r'^new/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp.new'),
        (r'^edit/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp.edit'),        
        (r'^view/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.rsvp.view'),        
        (r'^edit_ajax/$', 'hkn.event.rsvp.rsvp.edit_ajax'),       
        
        # list views
        (r'^list_event/(?P<event_id>.*)/$', 'hkn.event.rsvp.list.list_for_event'),
        (r'^list_event/$', 'hkn.event.rsvp.list.list_for_event', {"event_id" : "-1"}),        
        (r'^list_for_event_ajax/$', 'hkn.event.rsvp.list.list_for_event_ajax'),
        
        (r'^list_person/(?P<person_id>.*)/$', 'hkn.event.rsvp.list.list_for_person'),        
        (r'^list_person/$', 'hkn.event.rsvp.list.list_for_person', {"person_id" : ""}),
        (r'^mine/$', 'hkn.event.rsvp.list.list_for_person', {"person_id" : ""}),
        (r'^list_for_person_ajax/$', 'hkn.event.rsvp.list.list_for_person_ajax'), 
    
        )