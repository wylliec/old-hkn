from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from hkn.course.models import *

from hkn.list import get_list_context, filter_objects

from string import atoi

def find_course(request):
    list_context = get_list_context(request, default_sort = "department_abbr", default_max = "20")
    query_function = lambda objects, query: Course.objects.query(query, objects = objects)
    (courses, pages) = filter_objects(Course, list_context, query_objects = query_function)
    return render_to_response("course/ajax/find_course.html", {"courses" : courses}, context_instance = RequestContext(request))
    