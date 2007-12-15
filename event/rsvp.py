from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def message(request, msg):
	return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def rsvpFromFormInstance(form, rsvp = RSVP()):
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

def rsvpFormInstance(event, data = {}):
	form = RSVPForm(data)


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

def my_rsvps(request):
	#rsvps = RSVP.future.filter(person = request.user.person).select_related()
	rsvps = RSVP.objects.filter(person = request.user.person).select_related()

	return render_to_response('event/rsvp/my_rsvps.html', {"rsvps" : rsvps}, context_instance = RequestContext(request))

def list(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	rsvps = e.rsvp_set.select_related()
	return render_to_response("event/rsvp/list.html", {"rsvps" : rsvps, "event" : e}, context_instance = RequestContext(request))
	

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
	
def rsvp(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	if e.rsvp_type == RSVP_TYPE.NONE:
		return message(request, "Event " + e.name + " does not require RSVP!")

	person = request.user.person

	try:
		rsvp = RSVP.objects.get(event = e, person = person)
	except RSVP.DoesNotExist:
		rsvp = RSVP(event = e, person = person)

	if request.POST:
		form = rsvpFormInstance(e, request.POST)
		if form.is_valid():
			rsvp = rsvpFromFormInstance(form, rsvp)
			rsvp.save()
			return HttpResponseRedirect("/event/rsvp/mine")
	else:
		form = rsvpFormInstance(e, rsvp.__dict__)

	d = {"person" : person, "event" : e, "form" : form}

	return render_to_response('event/rsvp/rsvp.html', d, context_instance = RequestContext(request))

def rsvp_form(request):
	person = request.user.person


	if not request.POST or not request.POST.has_key("event_id"):
		return HttpResponse("no post")

	eid = atoi(request.POST["event_id"])
	try:
		e = Event.objects.get(pk = eid)
	except Event.DoesNotExist:
		return HttpResponse("sorry")

	try:
		rsvp = RSVP.objects.get(event = e, person = person)
	except RSVP.DoesNotExist:
		rsvp = RSVP(event = e, person = person)
	if request.POST.has_key("comment"):
		form = rsvpFormInstance(e, request.POST)
		if form.is_valid():
			rsvp = rsvpFromFormInstance(form, rsvp)
			rsvp.save()
			return HttpResponse("<BR><B>Successfully RSVPd for " + e.name + "</B>")
	else:
		form = rsvpFormInstance(e, rsvp.__dict__)

	d = {"person" : person, "event" : e, "form" : form}

	return render_to_response('event/rsvp/ajax/rsvp.html', d, context_instance = RequestContext(request))

