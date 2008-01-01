from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def message(request, msg):
	return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def event_from_form_instance(form, event = Event()):
	cd = form.clean_data
	for k in cd.keys():
		setattr(event, k, cd[k])

	if event.gcal_id == None:
		event.gcal_id = ""
	return event

def edit(request, event_id = "-1"):
	new = False
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		e = Event()
		new = True
	
	if request.POST:
		form = EventForm(request.POST)
		if form.is_valid():
			e = event_from_form_instance(form, e)
			e.save()
			return HttpResponseRedirect("/event/list")
	else:
		if new:
			form = EventForm()
		else:
			form = EventForm(e.__dict__)
	
	return render_to_response("event/edit.html", {"form" : form}, context_instance=RequestContext(request))

def new(request):
	return edit(request, "-1")

def view(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	return render_to_response("event/view.html", {"event" : e}, context_instance=RequestContext(request))

def delete(request, event_id = "-1"):
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	name = e.name
	e.delete()

	return message(request, "Event " + name + " successfully deleted!")

def calendar(request):
	return render_to_response('event/calendar.html', context_instance = RequestContext(request))