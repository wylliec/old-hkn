from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core import urlresolvers
from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.decorators import *
from hkn.list import get_list_context, filter_objects
from string import atoi


@login_required
#@permission_required("all.view.basic")
def list_people(request, category):
	d = get_list_context(request, default_sort = "first", default_category = category)	
	d["objects_url"] = urlresolvers.reverse("hkn.info.list.list_people_ajax")	
	return render_to_response("list/list.html", d, context_instance=RequestContext(request))

def list_people_ajax(request):
	list_context = get_list_context(request, default_sort = "first")
	query_people = lambda objects, query: Person.objects.query(query, objects)
	(people, pages) = filter_objects(Person, list_context, query_objects = query_people, category_map = {"all" : "objects"})
	
	list_context["people"] = people
	list_context["page_range"] = range(1, pages+1)
	return render_to_response("info/ajax/list_people.html", list_context, context_instance = RequestContext(request))

