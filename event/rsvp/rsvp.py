from hkn.event.models import *
from hkn.event.forms import *
from hkn.request.models import *
from hkn.request.constants import REQUEST_TYPE

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.shortcuts import get_object_or_404

from ajaxlist import get_list_context, filter_objects

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def message(request, msg):
    return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def rsvp_from_form_instance(form, rsvp = RSVP()):
    cd = form.clean_data
    if cd.has_key('comment'):
        rsvp.comment = cd['comment']
    else:
        rsvp.comment = ""
    if cd.has_key('transport'):
        rsvp.transport = cd['transport']
    else:
        rsvp.transport = 0
    if cd.has_key('rsvp_data'):
        rsvp.set_rsvp_data(RSVPData(cd['rsvp_data']))
    else:
        rsvp.rsvp_data_pkl = ""
    

    return rsvp

def rsvp_form_instance(event, data = {}):
    if data:
        form = RSVPForm(data)
    else:
        form = RSVPForm()

    if event.rsvp_transportation_necessary:
        form.fields['transport'] = forms.IntegerField(label = "Transport (0 for none)")
        form.fields['transport'].required = True
        form.fields['transport'].widget = forms.TextInput()
    if event.rsvp_type == RSVP_TYPE.BLOCK:
        form.fields['rsvp_data'] = RSVPDataField(label = "Block RSVPs")
        form.fields['rsvp_data'].required = True
        form.fields['rsvp_data'].widget = forms.CheckboxSelectMultiple()
        form.fields['rsvp_data'].bindEvent(event)

    return form	

def delete(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)
    

    if rsvp.person_id != request.user.person_id:
        return message(request, "Can't delete someone else's RSVP!")

    rsvp.delete()
    

    return message(request, "Your RSVP for event " + str(e.name) + " has been deleted!")

def request_confirmation(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)
    

    if rsvp.person_id != request.user.person_id:
        return message(request, "Can't request to confirm for RSVP!")
    

    req = Request.objects.request_confirmation(REQUEST_TYPE.RSVP, rsvp, request.user.person)
    req.save()
    

    return message(request, "You have requested a confirmation for this RSVP.")

def view(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)

    d = {"rsvp" : rsvp, "person" : rsvp.person, "event" : rsvp.event}

    return render_to_response("event/rsvp/view.html", d, context_instance = RequestContext(request))
    

def edit(request, event_id = "-1"):
    e = get_object_or_404(Event, pk = event_id)

    if e.rsvp_type == RSVP_TYPE.NONE:
        return message(request, "Event " + e.name + " does not require RSVP!")

    person = request.user.person

    new = False
    try:
        rsvp = RSVP.objects.get(event = e, person = person)
    except RSVP.DoesNotExist:
        rsvp = RSVP(event = e, person = person)
        new = True

    if request.POST:
        form = rsvp_form_instance(e, request.POST)
        if form.is_valid():
            rsvp = rsvp_from_form_instance(form, rsvp)
            rsvp.save()
            return HttpResponseRedirect("/event/rsvp/mine")
    else:
        if new:
            form = rsvp_form_instance(e)
        else:
            form = rsvp_form_instance(e, rsvp.__dict__)

    d = {"person" : person, "event" : e, "form" : form}

    return render_to_response('event/rsvp/edit.html', d, context_instance = RequestContext(request))

def new(request, event_id):
    return edit(request, event_id)

def edit_ajax(request):
    person = request.user.person

    if not request.POST or not request.POST.has_key("event_id"):
        return HttpResponse("no post or no event_id in post")

    event_id = atoi(request.POST["event_id"])
    e = get_object_or_404(Event, pk = event_id)

    new_rsvp = False
    try:
        rsvp = RSVP.objects.get(event = e, person = person)
    except RSVP.DoesNotExist:
        rsvp = RSVP(event = e, person = person)
        new_rsvp = True
        

    if request.POST.has_key("comment"):
        form = rsvp_form_instance(e, request.POST)
        if form.is_valid():
            rsvp = rsvp_from_form_instance(form, rsvp)
            rsvp.save()
            return HttpResponse("<BR/><strong>Successfully RSVPd for " + e.name + "</strong>")
    else:
        if new_rsvp:
            form = rsvp_form_instance(e)
        else:
            form = rsvp_form_instance(e, rsvp.__dict__)

    d = {"person" : person, "event" : e, "form" : form}

    return render_to_response('event/rsvp/ajax/edit_ajax.html', d, context_instance = RequestContext(request))

