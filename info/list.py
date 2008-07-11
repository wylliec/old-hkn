from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core import urlresolvers
from hkn.info.models import *
from hkn.info.utils import *
from django.contrib.auth.decorators import *
from ajaxlist import get_list_context, filter_objects
from string import atoi

def add_restricted(request, people):
    accessor = request.user.person
    people = list(people)
    [person.set_restricted_accessor(accessor) for person in people]
    return people

def get_list_people_context(request, category = None):
    list_context = get_list_context(request, default_sort = "first_name", default_category = category)
    query_people = lambda objects, query: objects.ft_query(query)
    filter_permissions = lambda objects: objects.filter_restricted(request.user)
    list_context["list_objects"] =  filter_objects(Person, list_context, query_objects = query_people, category_map = {"all" : "objects"}, filter_permissions=filter_permissions, final_filter=lambda people: add_restricted(request, people))
    list_context["header_template"] = "info/ajax/_list_people_header.html"
    list_context["row_template"] = "info/ajax/_list_people_row.html"
    return list_context

@login_required
def list_people(request, category):
    list_context = get_list_people_context(request, category)
    list_context["objects_url"] = urlresolvers.reverse("hkn.info.list.list_people_ajax")	
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance=RequestContext(request))

@login_required
def list_people_ajax(request):
    list_context = get_list_people_context(request)
    return render_to_response("ajaxlist/_objects_view.html", list_context, context_instance = RequestContext(request))

