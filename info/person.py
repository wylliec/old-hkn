from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from hkn.info.models import *
from hkn.event.rsvp.list import list_for_person_common
import datetime

@login_required
def view(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        person = get_object_or_404(Person, username=person_id)
    person.set_restricted_accessor(request.user.person)
    d = {}
    d["rsvps"] = person.rsvp_set.order_by("-event__start_time")[:7]
    d["person"] = person    
    return render_to_response("info/details.html", d, context_instance=RequestContext(request))

