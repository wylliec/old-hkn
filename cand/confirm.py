from hkn.cand.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.core import urlresolvers

from hkn.list import get_list_context, filter_objects

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def message(request, msg):
    return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def add_events_to_confirm_metainfo(events):
    for e in events:
        e.confirm = len(RSVP.objects.getConfirmedForEvent(e))
        e.possible = len(RSVP.objects.getConfirmablesForEvent(e))
    return events
    

def list_events_to_confirm(request, event_category):
    d = get_list_context(request, default_sort = "-start_time", default_category = event_category)    
    d["objects_url"] = urlresolvers.reverse("hkn.cand.confirm.list_events_to_confirm_ajax")
    return render_to_response("list/list.html", d, context_instance=RequestContext(request))

def filter_events_by_category(clazz, objects, category):
    try:
        objects = objects & clazz.__dict__[category].manager.all()
        return objects;
    except:
        pass
    

    category = category.upper()
    if not category in EVENT_TYPE:
        raise KeyError, "category does not exist!"   
    

    return objects.filter(event_type = category)

def get_events_for_categories(clazz, categories, category_map):
    objects = clazz._default_manager.filter(Q(rsvp_type = RSVP_TYPE.WHOLE) | Q(rsvp_type = RSVP_TYPE.BLOCK))
    if len(categories) == 0:
        return objects

    try:        
        for category in categories:
            category = category_map.get(category, category)            
            objects = filter_events_by_category(clazz, objects, category)            
    except KeyError, e:
        raise KeyError, "Category \"" + category + "\" does not exist for class " + clazz.__class__.__name__
    

    return objects

def list_events_to_confirm_ajax(request):
    list_context = get_list_context(request, default_sort = "-start_time")
    permissions = request.user.get_all_permissions()
    filter_permissions = lambda objects: objects.filter(view_permission__in = permissions)
    query_events = lambda objects, query: Event.objects.query(query, objects)
    (events, pages) = filter_objects(Event, list_context, query_objects = query_events, filter_permissions = filter_permissions, get_objects_for_categories = get_events_for_categories, final_filter = add_events_to_confirm_metainfo)
    

    list_context["events"] = events
    list_context["page_range"] = range(1, pages+1)
    

    return render_to_response("cand/ajax/list_events_to_confirm.html", list_context, context_instance = RequestContext(request))


def requirements(request):
    person = Person.objects.get(pk = request.user.person_id)
    confirmed_rsvps = RSVP.objects.getAttendedEvents(person = person)
    type_rsvp = {}
    for etype, value in EVENT_TYPE.items():
        type_rsvp[value] = confirmed_rsvps.filter(event__event_type__iexact = etype)
    return render_to_response("cand/requirements.html", {"type_rsvps" : type_rsvp}, context_instance = RequestContext(request))

