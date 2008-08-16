from hkn.event.models import *
from hkn.event.forms import *
from hkn.event.rsvp.list import list_for_event_common

from ajaxlist import get_list_context
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core import urlresolvers
from django import forms

from constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def view(request, event_id):
    e = get_object_or_404(Event, pk = event_id)
    d = {}
    d["event"] = e
        
    permission_name = "%s.%s" % (e.view_permission.content_type.app_label, e.view_permission.codename)
    if permission_name not in request.user.get_all_permissions():
        return render_to_response('main/access_denied.html', context_instance = RequestContext(request))
    
    if request.is_ajax():
        return render_to_response("event/view_ajax.html", d, context_instance = RequestContext(request))
    
    permission_name = "%s.%s" % (e.rsvp_permission.content_type.app_label, e.rsvp_permission.codename)
    if permission_name in request.user.get_all_permissions():
        d["can_rsvp"] = e.rsvp_set.filter(person = request.user.person).count() == 0
        
    d["rsvps"] = e.rsvp_set.select_related('person').order_by("person__first_name")
    return render_to_response("event/view.html", d, context_instance=RequestContext(request))

def infobox(request, event_id):
    e = get_object_or_404(Event, pk = event_id)
    if e.view_permission.full_codename() not in request.user.get_all_permissions():
        return HttpResponse("Access denied")
    d = {}
    d["event"] = e
    d["rsvps"] = e.rsvp_set.all()[:5]
    return render_to_response("event/infobox.html", d, context_instance=RequestContext(request))

def calendar(request):
    return render_to_response('event/calendar.html', context_instance = RequestContext(request))
