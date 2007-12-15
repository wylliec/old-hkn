from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from hkn.info.models import *

def find_person(request):
	if not request.GET or not request.GET.has_key("query"):
		return HttpResponse("")
	q = request.GET["query"].split(" ")

	people = Person.objects.none()
	for query in q:
		people |= Person.objects.filter(Q(first__icontains = query) | Q(last__icontains = query))
	
	return render_to_response("info/ajax/find_person.html", {"persons" : people}, context_instance = RequestContext(request))


