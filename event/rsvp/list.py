from django.contrib.auth.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django import forms
from django.core import urlresolvers
from ajaxlist import get_list_context, filter_objects

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE
import datetime
from string import atoi


sort_rsvps = lambda rsvps, sort_field: RSVP.objects.order(sort_field, rsvps) 
query_rsvps = lambda rsvps, query: RSVP.objects.query(query, rsvps)       
query_rsvps_by_event = lambda rsvps, query: RSVP.objects.query_event(query, rsvps)       
query_rsvps_by_person = lambda rsvps, query: RSVP.objects.query_person(query, rsvps)       

vp_perm = Permission.objects.get(codename = "group_vp")

def show_confirm_form(request):
    #return False
    return request.user.has_perm(vp_perm)



def get_rsvps_for_person(clazz, categories, category_map):
    objects = RSVP.objects.none()
    
    for category in categories:
        objects = objects | clazz.objects.filter(person = category)
        
    return objects

def get_rsvps_for_event(clazz, categories, category_map):
    objects = RSVP.objects.none()
    
    if len(categories) != 1:
        raise Exception, "Too many categories!"
    
    category = categories[0]
    return clazz.objects.filter(event = category)

def get_list_for_person_context(request, person_id = None):
    list_context = get_list_context(request, default_sort = "-event__start_time", default_category = person_id)
    list_context["rsvps"] = filter_objects(RSVP, list_context, get_objects_for_categories = get_rsvps_for_person, sort_objects = sort_rsvps, query_objects = query_rsvps_by_event)

    list_context["title"] = "HKN - RSVPs"
    list_context["show_confirm_form"] = show_confirm_form(request)
    list_context["view_template"] = "event/rsvp/ajax/_list_for_person.html"

    return (list_context, list_context["rsvps"], list_context["show_confirm_form"])
    

def list_for_person(request, person_id):
    if len(person_id) == 0 or person_id == "me":
        person_id = str(request.user.person.id)

    (list_context, rsvps, show_confirm_form) = get_list_for_person_context(request, person_id)
    list_context["objects_url"] = urlresolvers.reverse("hkn.event.rsvp.list.list_for_person_ajax")
    #if show_confirm_form(request):
    #    d["extra_javascript"] = "event/rsvp/ajax/list_rsvps_javascript.html"
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance = RequestContext(request))



def list_for_person_ajax(request):
    (list_context, rsvps, show_confirm_form) = get_list_for_person_context(request)

    if request.POST and show_confirm_form:
        for rsvp in rsvps:
            attr_confirm = str(rsvp.id) + ".vp_confirm"
            attr_comment = str(rsvp.id) + ".vp_comment"
            
            if request.POST.has_key(attr_comment):
                rsvp.vp_comment = request.POST[attr_comment]
                
            if request.POST.has_key(attr_confirm):
                rsvp.vp_confirm = True
            else:
                rsvp.vp_confirm = False
            
            rsvp.save()      
    
    list_context["rsvps"] = rsvps
    list_context["page_range"] = range(1, pages+1)
    list_context["show_confirm_form"] = show_confirm_form(request)
    
    return render_to_response("event/rsvp/ajax/_list_for_person.html", list_context, context_instance = RequestContext(request))

def get_list_for_event_context(request, event_id = None):
    list_context = get_list_context(request, default_sort = "person__first_name", default_category = event_id)
    list_context["rsvps"] = filter_objects(RSVP, list_context, get_objects_for_categories = get_rsvps_for_event, sort_objects = sort_rsvps, query_objects = query_rsvps_by_person)

    event_id = list_context["categories"][0]
    try:
        event = Event.objects.get(pk = event_id)
    except:
        event = None

    list_context["event"] = event    
    list_context["title"] = "HKN - RSVPs for " + event.name
    list_context["show_confirm_form"] = show_confirm_form(request)
    list_context["view_template"] = "event/rsvp/ajax/_list_for_event.html"

    return (list_context, list_context["show_confirm_form"])
    

def list_for_event(request, event_id):
    (list_context, show_confirm_form) = get_list_for_event_context(request, event_id)
    list_context["objects_url"] = urlresolvers.reverse("hkn.event.rsvp.list.list_for_event_ajax")
    #if show_confirm_form:
    #    d["extra_javascript"] = "event/rsvp/ajax/list_rsvps_javascript.html"    
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance = RequestContext(request))


def list_for_event_ajax(request):    
    (list_context, show_confirm_form) = get_list_for_event_context(request)
    rsvps = list_context["rsvps"]
        
    if request.POST and show_confirm_form:
        for rsvp in rsvps:
            attr_confirm = str(rsvp.id) + ".vp_confirm"
            attr_comment = str(rsvp.id) + ".vp_comment"
            
            if request.POST.has_key(attr_comment):
                rsvp.vp_comment = request.POST[attr_comment]
                
            if request.POST.has_key(attr_confirm):
                rsvp.vp_confirm = True
            else:
                rsvp.vp_confirm = False
            
            rsvp.save()        
    
    return render_to_response("event/rsvp/ajax/_list_for_event.html", list_context, context_instance = RequestContext(request))

def list_for_event_small_ajax(request):    
    list_context = get_list_context(request, default_sort = "person__first")
    (rsvps, pages) = filter_objects(RSVP, list_context, get_objects_for_categories = get_rsvps_for_event, sort_objects = sort_rsvps, query_objects = query_rsvps_by_person)

    categories = list_context["categories"]
    category = categories[0]
    try:
        event = Event.objects.get(pk = category)
    except:
        event = None    
    
    list_context["event"] = event    
    list_context["rsvps"] = rsvps
    
    
    return render_to_response("event/rsvp/ajax/list_for_event_small.html", list_context, context_instance = RequestContext(request))
