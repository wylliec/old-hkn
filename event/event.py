from hkn.event.models import *
from hkn.event.forms import *
from ajaxlist import get_list_context
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core import urlresolvers
from django import forms

from constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def view(request, event_id = "-1"):
    e = get_object_or_404(Event, pk = event_id)
    permission_name = "%s.%s" % (e.view_permission.content_type.app_label, e.view_permission.codename)
    if permission_name not in request.user.get_all_permissions():
        return render_to_response('main/access_denied.html', context_instance = RequestContext(request))
    d = get_list_context(request, default_sort = "person__first")
    d["event"] = e
    d["rsvps_url"] = urlresolvers.reverse("hkn.event.rsvp.list.list_for_event_small_ajax", kwargs = {"event_id" : event_id})	
    return render_to_response("event/view.html", d, context_instance=RequestContext(request))

def infobox(request, event_id):
    e = get_object_or_404(Event, pk = event_id)
    permission_name = "%s.%s" % (e.view_permission.content_type.app_label, e.view_permission.codename)
    if permission_name not in request.user.get_all_permissions():
        return render_to_response('main/access_denied.html', context_instance = RequestContext(request))
    d = {}
    d["event"] = e
    d["rsvps"] = e.rsvp_set.all()[:5]
    return render_to_response("event/infobox.html", d, context_instance=RequestContext(request))

def calendar(request):
    return render_to_response('event/calendar.html', context_instance = RequestContext(request))
