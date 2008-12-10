from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from hkn.info.models import *
from hkn.cand.models import *
from hkn.event.rsvp.list import list_for_person_common
import datetime

@login_required
def view(request, person_id):
    try:
        person = Person.objects.get(pk=int(person_id))
    except (Person.DoesNotExist, ValueError):
        person = get_object_or_404(Person, username=person_id)
    person.set_restricted_accessor(request.user.person)
    d = {}
    d["rsvps"] = person.rsvp_set.order_by("-event__start_time")[:7]
    d["person"] = person    
    d["membership_info"] = membership_info(person)
    return render_to_response("info/details.html", d, context_instance=RequestContext(request))

def membership_info(person):
    d = {}
    d['person'] = person
    d['officerships'] = person.officership_set.order_by('-semester')
    try:
        d['candidate_info'] = person.candidateinfo
        if len(d['officerships']) == 0 and not d['candidate_info'].initiated:
            d['no_info'] = True
    except CandidateInfo.DoesNotExist:
        d['no_info'] = True
    return render_to_string("info/_membership_info.html", d)
     
