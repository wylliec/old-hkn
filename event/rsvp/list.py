from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from hkn.list import get_list_context, filter_objects

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE
import datetime
from string import atoi


def list_for_person(request, person_id = ""):
    if len(person_id) == 0:
        person_id = str(request.user.person.person_id)
    
    #d = get_list_context(request, default_sort = "-event__start_time", default_category = person_id)
    d = get_list_context(request, default_sort = "?", default_category = person_id)    
    d["objects_url"] = "/event/rsvp/list_for_person_ajax"
    return render_to_response("list/list.html", d, context_instance = RequestContext(request))

def list_for_event(request, event_id = "-1"):
    d = get_list_context(request, default_sort = "?", default_category = event_id)
    #d = get_list_context(request, default_sort = "person__first", default_category = event_id)
    d["objects_url"] = "/event/rsvp/list_for_event_ajax"
    return render_to_response("list/list.html", d, context_instance = RequestContext(request))


def get_rsvps_for_person(clazz, categories, category_map):
    objects = RSVP.objects.none()
    
    for category in categories:
        objects = objects | clazz.objects.filter(person = category)
        
    return objects

def get_rsvps_for_event(clazz, categories, category_map):
    objects = RSVP.objects.none()
    
    for category in categories:
        objects = objects | clazz.objects.filter(event = category)
        
    return objects            
        

def list_for_person_ajax(request):    
    #list_context = get_list_context(request, default_sort = "-event__start_time")    
    list_context = get_list_context(request, default_sort = "")    
    (rsvps, pages) = filter_objects(RSVP, list_context, get_objects_for_categories = get_rsvps_for_person)
    
    list_context["rsvps"] = rsvps
    list_context["page_range"] = range(1, pages+1)
    
    return render_to_response("event/rsvp/ajax/list_for_person.html", list_context, context_instance = RequestContext(request))

def list_for_event_ajax(request):    
    list_context = get_list_context(request, default_sort = "?")    
#        list_context = get_list_context(request, default_sort = "person__first")    
    (rsvps, pages) = filter_objects(RSVP, list_context, get_objects_for_categories = get_rsvps_for_event)
    
    list_context["rsvps"] = rsvps
    list_context["page_range"] = range(1, pages+1)
    list_context["title"] = "RSVPs"
    
    return render_to_response("event/rsvp/ajax/list_for_event.html", list_context, context_instance = RequestContext(request))