from hkn.event.models import *
from hkn.event.forms import *
from hkn.event.rsvp.list import list_for_event_common
from hkn.event.constants import EVENT_TYPE
from hkn.event.rsvp.constants import RSVP_TYPE

from hkn.gcal import calendars

from ajaxlist import get_list_context
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core import urlresolvers
from django import forms


import datetime
from string import atoi


def get_event(event_identifier):
    try:
        return Event.objects.get(pk=event_identifier)
    except (Event.DoesNotExist, ValueError):
        return get_object_or_404(Event, slug=event_identifier)

def view(request, event_id):
    e = get_event(event_id)
    d = {}
    d["event"] = e
        
    permission_name = "%s.%s" % (e.view_permission.content_type.app_label, e.view_permission.codename)
    if permission_name not in request.user.get_all_permissions():
        return render_to_response('main/access_denied.html', context_instance = RequestContext(request))
    
    if request.is_ajax():
        return render_to_response("event/view_ajax.html", d, context_instance = RequestContext(request))
    
    permission_name = "%s.%s" % (e.rsvp_permission.content_type.app_label, e.rsvp_permission.codename)
    if getattr(request.user, 'person', False) and permission_name in request.user.get_all_permissions():
        d["can_rsvp"] = e.rsvp_set.filter(person = request.user.person).count() == 0 and not e.rsvp_none()
        
    d["rsvps"] = e.rsvp_set.select_related('person').order_by("person__first_name")
    return render_to_response("event/view.html", d, context_instance=RequestContext(request))

def infobox(request, event_id):
    e = get_event(event_id)
    if e.view_permission.full_codename() not in request.user.get_all_permissions():
        return HttpResponse("Access denied")
    d = {}
    d["event"] = e
    d["rsvps"] = e.rsvp_set.all()[:5]
    return render_to_response("event/infobox.html", d, context_instance=RequestContext(request))

def calendar(request):
    #d = {'ical' : calendars.calendars[0].get_ical_link()}
    d = {'event_types': [(type, EVENT_TYPE[type]) for type in EVENT_TYPE.values()]}
    return render_to_response('event/calendar.html', d, context_instance = RequestContext(request))


def event_autocomplete(request, manager):
    def iter_results(events):
        if events:
            for e in events:
                yield '%s|%s\n' % (e.name, e.id)
    
    if not request.GET.get('q'):
        return HttpResponse(mimetype='text/plain')
    
    q = request.GET.get('q')
    limit = request.GET.get('limit', 15)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    if manager == 'current_semester':
        events = Event.semester.ft_query(q)[:limit]
    return HttpResponse(iter_results(events), mimetype='text/plain')

