from hkn.cand.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE
from hkn import semester

import datetime
from string import atoi

def message(request, msg):
	return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def initiate(request):

	candidates = Person.objects.filter(candidateinfo__candidate_semester__iexact = semester.getCurrentSemester())


	if request.POST:
		for c in candidates:
			attr_initiated = str(c.person_id) + ".initiated"
			attr_comment = str(c.person_id) + ".comment"

			if not request.POST.has_key(attr_comment):
				return message("No comment field for candidate: " + str(c.name()))

			ci = c.candidateinfo
			ci.initiation_comment = request.POST[attr_comment]
			ci.save()

			c.initiate(request.POST.has_key(attr_initiated))
			c.save()

	for c in candidates:
		c.comment = c.candidateinfo.initiation_comment
		c.events_attended = len(RSVP.objects.getConfirmedEvents(c))

	return render_to_response("cand/initiate.html", {"candidates" : candidates}, context_instance = RequestContext(request))
