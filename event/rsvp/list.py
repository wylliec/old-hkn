from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django import forms
from django.core import urlresolvers
from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response, render_ajaxwrapper_response

from hkn.event.constants import EVENT_TYPE
from hkn.event.rsvp.constants import RSVP_TYPE
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

def list_for_person_common(request, person, all=False, max_per_page=None):
    d = get_ajaxinfo(request.POST)
    if d['sort_by'] == "?":
        d['sort_by'] = "-event__start_time"
    
    if all:
        rsvps = person.rsvp_set.filter(event__start_time__gte = (datetime.date.today()-datetime.timedelta(days = 1)))
    else:
        rsvps = person.rsvp_set.all()
    
    rsvps = sort_objects(rsvps, d['sort_by'], None)
    rsvps = paginate_objects(rsvps, d, page=d['page'], max_per_page=max_per_page)

    d['rsvps'] = rsvps    
    return d

#@login_required
def list_for_person_small_ajax(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    d = list_for_person_common(request, person, max_per_page=5)    
    return render_ajaxwrapper_response("event/rsvp/ajax/_list_for_person_small.html", d, context_instance=RequestContext(request))

@login_required
def list_for_person(request, person_id):
    if len(person_id) == 0 or person_id == "me":
        person = request.user.person
    else:
        person = get_object_or_404(Person, pk=person_id)
    
    d = list_for_person_common(request, person)
    d['person'] = person	
    d['show_confirm_form'] = show_confirm_form(request)
	
    return render_ajaxlist_response(request.is_ajax(), "event/rsvp/list_for_person.html", d, context_instance=RequestContext(request))
    
def list_for_event_common(request, event):    
    d = get_ajaxinfo(request.POST)
    if d['sort_by'] == "?":
        d['sort_by'] = "person__first_name"
        
    rsvps = event.rsvp_set.all()

    transport = 0
    for rsvp in rsvps:
        transport += rsvp.transport
    d['transport'] = transport
    
    rsvps = sort_objects(rsvps, d['sort_by'], None)
    rsvps = paginate_objects(rsvps, d, page=d['page'], max_per_page=100)

    d['rsvps'] = rsvps
    return d
    
def list_for_event(request,  event_id):
    event = get_object_or_404(Event, pk=event_id)    
    d = list_for_event_common(request, event)
    d['event'] = event    
    d['show_confirm_form'] = show_confirm_form(request)
	
    return render_ajaxlist_response(request.is_ajax(), "event/rsvp/list_for_event.html", d, context_instance=RequestContext(request))

def list_for_event_small_ajax(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    d = list_for_event_common(request, event)    
    return render_ajaxwrapper_response("event/rsvp/_list_for_event_small.html", d, context_instance=RequestContext(request))

def list_for_event_paragraph(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    rsvp_text = ", ".join([r.person.get_abbr_name(dot=False) for r in event.rsvp_set.select_related('person').order_by("person__first_name")])
    return HttpResponse(rsvp_text, mimetype="text/plain")    

@permission_required('info.group_vp')
def confirm_ajax_check(request):
    if not request.POST:
        return
    
    action = request.POST.get("value", None)
    if not action or action == "unknown":
        return

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


@permission_required('info.group_vp')    
def confirm_ajax(request, add_or_remove):
    if not request.POST:
        return

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
    
    
    
