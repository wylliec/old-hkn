from django.conf.urls.defaults import *

urlpatterns = patterns('',
        
        # standard new, edit, delete views
        url(r'^delete/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.rsvp.delete', name="rsvp-delete"),
        url(r'^new/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp.new', name="rsvp-new"),
        url(r'^edit/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp.edit', name="rsvp-edit"),
        url(r'^edit-ajax/(?P<event_id>.*)/$', 'hkn.event.rsvp.rsvp.edit_ajax', name="rsvp-edit-ajax"),        
        url(r'^view/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.rsvp.view', name="rsvp-view"),        
        url(r'^request_confirmation/(?P<rsvp_id>.*)/$', 'hkn.event.rsvp.rsvp.request_confirmation', name="rsvp-request-confirmation"),                
        #url(r'^edit_ajax/$', 'hkn.event.rsvp.rsvp.edit_ajax', name="rsvp-edit-ajax"),       

        url(r'^list_for_event_paragraph/(?P<event_id>.*)/$', 'hkn.event.rsvp.list.list_for_event_paragraph', name="rsvp-list-for-event-paragraph"),
        
        # list views
        url(r'^list_event/(?P<event_id>.*)/$', 'hkn.event.rsvp.list.list_for_event', name="rsvp-list-for-event"),
        url(r'^list_event/$', 'hkn.event.rsvp.list.list_for_event', {"event_id" : "-1"}),
        url(r'^list_for_event_small_ajax/(?P<event_id>.*)/$', 'hkn.event.rsvp.list.list_for_event_small_ajax', name="rsvp-list-for-event-small"),
        url(r'^list_for_person_small_ajax/(?P<person_id>.*)/$', 'hkn.event.rsvp.list.list_for_person_small_ajax', name="rsvp-list-for-person-small"),
        
        url(r'^list_person/(?P<person_id>.*)/$', 'hkn.event.rsvp.list.list_for_person', name="rsvp-list-for-person"),
        url(r'^list_person/$', 'hkn.event.rsvp.list.list_for_person', {"person_id" : "-1"}, name="rsvp-list-for-self"),
        url(r'^mine/$', 'hkn.event.rsvp.list.list_for_person', {"person_id" : ""}, name="rsvp-list-mine"),
        url(r'^confirm_ajax/$', 'hkn.event.rsvp.list.confirm_ajax', name="rsvp-confirm"),        
        url(r'^confirm_ajax/(?P<add_or_remove>\w*)/$', 'hkn.event.rsvp.list.confirm_ajax', name="rsvp-confirm-full"),
    
        )
