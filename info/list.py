from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.decorators import *
from hkn.list import get_list_context, filter_objects
from string import atoi


@login_required
#@permission_required("all.view.basic")
def list_people(request, person_class):
	d = get_list_context(request, default_sort = "first", default_category = person_class)	
	d["objects_url"] = "/info/list_people_ajax"
	return render_to_response("list/list.html", d, context_instance=RequestContext(request))

def query_people(objects, query):
	persons = objects
	if query and len(query.strip()) != 0:
		for q in query.split(" "):
			if len(q.strip()) == 0:
				continue
			persons = persons.filter(Q(first__icontains = q) | Q(last__icontains = q) | Q(user__username__icontains = q))
	return persons

def list_people_ajax(request):
	list_context = get_list_context(request, default_sort = "first")
	(people, pages) = filter_objects(Person, list_context, query_objects = query_people, category_map = {"all" : "objects"})
	
	list_context["people"] = people
	list_context["page_range"] = range(1, pages+1)
	return render_to_response("info/ajax/list_people.html", list_context, context_instance = RequestContext(request))

