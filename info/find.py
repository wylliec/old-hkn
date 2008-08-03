from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from hkn.info.models import *

from ajaxlist import get_list_context, filter_objects

from string import atoi


def find_person(request):
    list_context = get_list_context(request, default_sort = "first", default_max = "20")
    query_function = lambda objects, query: objects.ft_query(query)
    (people, pages) = filter_objects(Person, list_context, query_objects = query_function)
    return render_to_response("info/ajax/find_person.html", {"people" : people}, context_instance = RequestContext(request))


    



