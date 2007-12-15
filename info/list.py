from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.decorators import *
from string import atoi

@login_required
#@permission_required("all.view.basic")
def list_people(request, person_class, page = "1", max = "20"):
	sort_field = request.GET.get("sort", "first")

	try:
		page = atoi(page)
	except ValueError:
		page = 1

	try:
		max = atoi(max)
	except ValueError:
		max = 20

	descending = sort_field[0] == '-'
	sort_field_base = sort_field
	sort_character = None
	if descending:
		sort_character = False
		sort_field_base = sort_field_base[1:]
	else:
		sort_character = '-'
	
	persons = None
	if person_class == "all":
		persons = Person.objects.order_by(sort_field)
	elif person_class == "officers":
		persons = Person.officers.order_by(sort_field)
	elif person_class == "candidates":
		persons = Person.candidates.order_by(sort_field)
	elif person_class == "members":
		persons = Person.members.order_by(sort_field)

	if request.GET.has_key("cand_committee"):
		persons = persons.filter(candidateinfo__candidate_committee = Position.objects.getPosition(request.GET["cand_committee"]))

	if request.GET.has_key("query"):
		query = request.GET["query"]
		persons = persons.filter(Q(first__icontains = query) | Q(last__icontains = query))

	paginator = ObjectPaginator(persons, max)
	people = paginator.get_page(page-1)
	d = { "persons" : people, sort_field_base + "_order" : sort_character, "page_range" : range(1,paginator.pages+1), "class" : person_class, "max" : max, "page" : page }
	
	return render_to_response("info/list.html", d, context_instance=RequestContext(request))

