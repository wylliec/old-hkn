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

def eventFromFormInstance(form, event = Event()):
	cd = form.clean_data
	for k in cd.keys():
		setattr(event, k, cd[k])

	if event.gcal_id == None:
		event.gcal_id = ""
	return event


def new(request):

	if request.POST:
		form = EventForm(request.POST)
		if form.is_valid():
			event = eventFromFormInstance(form)
			event.save()
			return HttpResponseRedirect("/event/list")
	else:
		form = EventForm()
	
	return render_to_response("event/new.html", {"form" : form}, context_instance=RequestContext(request))


def edit(request, event_id = "-1"):
	e = None
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return HttpResponseRedirect("/event/new")
	
	if request.POST:
		form = EventForm(request.POST)
		if form.is_valid():
			e = eventFromFormInstance(form, e)
			e.save()
			return HttpResponseRedirect("/event/list")
	else:
		form = EventForm(e.__dict__)
	
	return render_to_response("event/new.html", {"form" : form}, context_instance=RequestContext(request))

	
def list(request):
	max = 300
	page = 1

	user = request.user
	permissions = user.get_all_permissions()

	start_time = datetime.date.today() - datetime.timedelta(days = 1)


#	events = Event.objects.order_by('start_time').filter(start_time__gte = start_time).filter(view_permission__in = permissions)
	events = Event.objects.order_by('-start_time').filter(view_permission__in = permissions)

	if request.GET and request.GET.has_key("event_type"):
		etype = request.GET["event_type"].upper()
		if not etype in EVENT_TYPE.CHOICES_DICT:
			return message("Invalid event type: " + str(etype))
		events = events.filter(event_type = etype)

	paginator = ObjectPaginator(events, max)
	events_to_display = paginator.get_page(page-1)
	d = {"events" : events_to_display}
	return render_to_response("event/list.html", d, context_instance=RequestContext(request))

def delete(request, event_id = "-1"):
	e = None
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	name = e.name
	e.delete()

	return message(request, "Event " + name + " successfully deleted!")

def calendar(request):
	return render_to_response('event/calendar.html', context_instance = RequestContext(request))
