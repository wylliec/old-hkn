from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from hkn.info.models import *

def details(request, id):
	person = get_object_or_404(Person, person_id = id)
	info = person.extendedinfo
	d = { "person" : person, "info" : info }
	return render_to_response("info/details.html", d, context_instance=RequestContext(request))

def pictures(request, id):
	person = get_object_or_404(Person, person_id = id)
	d = { "person" : person }
	return render_to_response("info/picture.html", d, context_instance=RequestContext(request))
