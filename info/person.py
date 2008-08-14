from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from hkn.info.models import *

def view(request, person_id):
    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        person = get_object_or_404(Person, username=person_id)
    person.set_restricted_accessor(request.user.person)
    d = { "person" : person }
    return render_to_response("info/details.html", d, context_instance=RequestContext(request))

def pictures(request, person_id):
    person = get_object_or_404(Person, pk = person_id)
    person.set_restricted_accessor(request.user.person)    
    d = { "person" : person }
    return render_to_response("info/picture.html", d, context_instance=RequestContext(request))
