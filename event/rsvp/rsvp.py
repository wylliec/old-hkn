from hkn.event.models import *
from hkn.event.forms import *

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django import forms
from django.shortcuts import get_object_or_404

from ajaxlist import get_list_context, filter_objects

from hkn.event.rsvp.list import list_for_person

from hkn.event.constants import EVENT_TYPE
from hkn.event.rsvp.constants import RSVP_TYPE, TRANSPORT
from hkn.info.constants import MEMBER_TYPE

import datetime
from string import atoi

def rsvp_from_form_instance(form, rsvp = RSVP()):
    cd = form.cleaned_data
    if cd.has_key('comment'):
        rsvp.comment = cd['comment']
    else:
        rsvp.comment = ""
    if cd.has_key('transport'):
        rsvp.transport = cd['transport']
    else:
        rsvp.transport = 0
    if cd.has_key('rsvp_data'):
        rsvp.rsvp_data = RSVPData(cd['rsvp_data'])
    else:
        rsvp.rsvp_data = ""
    

    return rsvp

def rsvp_form_instance(event, data = {}):
    if data:
        form = RSVPForm(data)
    else:
        form = RSVPForm()

    if event.rsvp_transportation_necessary:
        form.fields['transport'] = forms.IntegerField(label = "Transportation")
        form.fields['transport'].required = True
        form.fields['transport'].widget = forms.Select(choices = TRANSPORT.choices())
        form.fields['transport'].initial = -1
        form.fields.keyOrder = ['transport', 'comment']
    if event.rsvp_type == RSVP_TYPE.BLOCK:
        form.fields['rsvp_data'] = RSVPDataField(label = "Block RSVPs")
        form.fields['rsvp_data'].required = True
        form.fields['rsvp_data'].widget = forms.CheckboxSelectMultiple()
        form.fields['rsvp_data'].bindEvent(event)

    return form	

@login_required
def delete(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)
    

    if rsvp.person_id != request.user.id:
        request.user.message_set.create(message="Can't delete someone else's RSVP!")
    else:
        rsvp.delete()
        request.user.message_set.create(message="Your RSVP for %s has been deleted" % str(rsvp.event.name))
    
    return HttpResponseRedirect(reverse("rsvp-list-for-person", kwargs={"person_id" :"me"}))


@login_required
def request_confirmation(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)
    

    if rsvp.person_id != request.user.id:
        request.user.message_set.create(message="Can't request to confirm someone else's RSVP!")
    else:
        rsvp.request_confirmation()
        request.user.message_set.create(message="You have requested a confirmation for your RSVP for %s" % str(rsvp.event.name))

    return HttpResponseRedirect(reverse("rsvp-list-for-person", kwargs={"person_id" :"me"}))

@login_required
def view(request, rsvp_id = "-1"):
    rsvp = get_object_or_404(RSVP, pk = rsvp_id)

    d = {"rsvp" : rsvp, "person" : rsvp.person, "event" : rsvp.event}

    return render_to_response("event/rsvp/view.html", d, context_instance = RequestContext(request))
    

def edit2(request, event_id = "-1"):
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
            if person.member_type == MEMBER_TYPE.CANDIDATE:
                rsvp.request_confirmation()
            return HttpResponseRedirect("/event/rsvp/mine")
    else:
        if new:
            form = rsvp_form_instance(e)
        else:
            form = rsvp_form_instance(e, rsvp.__dict__)

    d = {"person" : person, "event" : e, "form" : form}

    return render_to_response('event/rsvp/edit.html', d, context_instance = RequestContext(request))

@login_required
def new(request, event_id):
    return edit(request, event_id)

@login_required
def edit(request, event_id):
    e = get_object_or_404(Event, pk = event_id)
    person = request.user.person

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
            if person.member_type == MEMBER_TYPE.CANDIDATE:
                rsvp.request_confirmation()
            request.user.message_set.create(message="Successfully RSVPd for %s" % str(e.name))
            return HttpResponseRedirect(reverse("rsvp-list-for-person", kwargs={"person_id" :"me"}))
    else:
        if new_rsvp:
            form = rsvp_form_instance(e)
        else:
            form = rsvp_form_instance(e, rsvp.__dict__)

    d = {"person" : person, "event" : e, "form" : form}

    if request.is_ajax():
        return render_to_response('event/rsvp/edit_ajax.html', d, context_instance = RequestContext(request))
    else:
        return render_to_response('event/rsvp/edit.html', d, context_instance = RequestContext(request))

@login_required
def edit_ajax(request, event_id):
    e = get_object_or_404(Event, pk = event_id)
    person = request.user.person

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
            #if user is a candidate, auto-request VP for confirmation
            if person.member_type == MEMBER_TYPE.CANDIDATE:
                rsvp.request_confirmation()
            return HttpResponse("rsvpCallback(%d);" % e.id, mimetype="text/javascript", status=200)
    else:
        if new_rsvp:
            form = rsvp_form_instance(e)
        else:
            form = rsvp_form_instance(e, rsvp.__dict__)

    d = {"person" : person, "event" : e, "form" : form }
    

    return render_to_response('event/rsvp/edit_ajax.html', d, context_instance = RequestContext(request))
