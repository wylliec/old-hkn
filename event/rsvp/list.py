from django.contrib.auth.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django import forms
from django.core import urlresolvers
from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response

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

def get_rsvps_for_event(clazz, categories, category_map):
    objects = RSVP.objects.none()
    
    if len(categories) != 1:
        raise Exception, "Too many categories!"
    
    category = categories[0]
    return clazz.objects.filter(event = category)

def list_for_person(request, person_id):
    if len(person_id) == 0 or person_id == "me":
        person_id = str(request.user.person.id)
    d = get_ajaxinfo(request.POST)
    if d['sort_by'] == "?":
        d['sort_by'] = "-event__start_time"
		
    person = get_object_or_404(Person, pk=person_id)
    rsvps = person.rsvp_set.all()
	
    rsvps = sort_objects(rsvps, d['sort_by'], None)
    rsvps = paginate_objects(rsvps, d, page=d['page'])

    d['rsvps'] = rsvps
    d['person'] = person	
    d['show_confirm_form'] = show_confirm_form(request)
	
    return render_ajaxlist_response(request.is_ajax(), "event/rsvp/list_for_person.html", d, context_instance=RequestContext(request))
    
def list_for_event(request,  event_id):
    d = get_ajaxinfo(request.POST)
    if d['sort_by'] == "?":
        d['sort_by'] = "person__first_name"
		
    event = get_object_or_404(Event, pk=event_id)
    rsvps = event.rsvp_set.all()
	
    rsvps = sort_objects(rsvps, d['sort_by'], None)
    rsvps = paginate_objects(rsvps, d, page=d['page'])

    d['rsvps'] = rsvps
    d['event'] = event
    d['show_confirm_form'] = show_confirm_form(request)
	
    return render_ajaxlist_response(request.is_ajax(), "event/rsvp/list_for_event.html", d, context_instance=RequestContext(request))

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
    
def confirm_ajax(request, add_or_remove):
    value = request.POST.get("value", None)
    if not value:
        return
    rsvp = get_object_or_404(RSVP, pk=value)
    if add_or_remove == "add":
        rsvp.vp_confirm = True
    else:
        rsvp.vp_confirm = False
    rsvp.save()
    return HttpResponse("success")
    
    
    
