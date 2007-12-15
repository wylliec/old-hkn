from hkn.cand.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE

import datetime
from string import atoi

def message(request, msg):
	return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def confirm(request, event_id = "-1"):
	e = None
	try:
		e = Event.objects.get(pk = event_id)
	except Event.DoesNotExist:
		return message(request, "Event with id " + str(event_id) + " does not exist!")

	rsvps = RSVP.objects.getConfirmablesForEvent(e)

	if request.POST:
		for rsvp in rsvps:
			attr_confirm = str(rsvp.rsvp_id) + ".vp_confirm"
			attr_comment = str(rsvp.rsvp_id) + ".vp_comment"
			if not request.POST.has_key(attr_comment):
				return message("No comment field for rsvp: " + str(rsvp.rsvp_id))
			else:
				rsvp.vp_comment = request.POST[attr_comment]

			if request.POST.has_key(attr_confirm):
				rsvp.vp_confirm = True
			else:
				rsvp.vp_confirm = False

		for rsvp in rsvps:
			rsvp.save()

	return render_to_response("cand/confirm.html", {"rsvps" : rsvps}, context_instance = RequestContext(request))

def list(request):
	max = 300
	page = 1

	user = request.user
	permissions = user.get_all_permissions()

	events = Event.past.order_by('-start_time').filter(Q(rsvp_type = RSVP_TYPE.WHOLE) | Q(rsvp_type = RSVP_TYPE.BLOCK))

	paginator = ObjectPaginator(events, max)
	events_to_display = paginator.get_page(page-1)

	for e in events_to_display:
		e.confirm = len(RSVP.objects.getConfirmedForEvent(e))
		e.possible = len(RSVP.objects.getConfirmablesForEvent(e))

	d = {"events" : events_to_display}
	return render_to_response("cand/list.html", d, context_instance=RequestContext(request))

def requirements(request):
	person = Person.objects.get(pk = request.user.person_id)
	confirmed_rsvps = RSVP.objects.getAttendedEvents(person = person)
	type_rsvp = {}
	for etype in EVENT_TYPE.CHOICES_DICT.keys():
		type_rsvp[EVENT_TYPE.CHOICES_DICT[etype]] = confirmed_rsvps.filter(event__event_type__iexact = etype)
	return render_to_response("cand/requirements.html", {"type_rsvps" : type_rsvp}, context_instance = RequestContext(request))

