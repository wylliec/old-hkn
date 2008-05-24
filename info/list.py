from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core import urlresolvers
from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.decorators import *
from ajaxlist import get_list_context, filter_objects
from string import atoi

def get_list_people_context(request, category = None):
    list_context = get_list_context(request, default_sort = "first", default_category = category)
    query_people = lambda objects, query: Person.objects.query(query, objects)
    list_context["list_objects"] =  filter_objects(Person, list_context, query_objects = query_people, category_map = {"all" : "objects"})
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

