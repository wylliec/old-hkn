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

def delete(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	person = request.user.person

	try:
		rsvp = RSVP.objects.get(event = e, person = person)
	except RSVP.DoesNotExist:
		return message(request, "RSVP for current used and event with id " + str(event_id) + " does not exist!")

	rsvp.delete()

	return message(request, "Your RSVP for event " + str(e.name) + " has been deleted!")

def view(request, rsvp_id = "-1"):
	try:
		rsvp = RSVP.objects.get(pk = rsvp_id)
	except RSVP.DoesNotExist:
		return message(request, "RSVP with id " + str(rsvp_id) + " does not exist!")

	d = {"rsvp" : rsvp, "person" : rsvp.person, "event" : rsvp.event}

	return render_to_response("event/rsvp/view.html", d, context_instance = RequestContext(request))
	
def edit(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

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

def new(request):
	return edit(request, "-1")

def new_ajax(request):
	person = request.user.person

	if not request.POST or not request.POST.has_key("event_id"):
		return HttpResponse("no post")

	eid = atoi(request.POST["event_id"])
	try:
		e = Event.objects.get(pk = eid)
	except Event.DoesNotExist:
		return HttpResponse("sorry")

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
			return HttpResponse("<BR><B>Successfully RSVPd for " + e.name + "</B>")
	else:
		if new_rsvp:
			form = rsvp_form_instance(e)
		else:
			form = rsvp_form_instance(e, rsvp.__dict__)

	d = {"person" : person, "event" : e, "form" : form}

	return render_to_response('event/rsvp/ajax/rsvp_new_ajax.html', d, context_instance = RequestContext(request))

