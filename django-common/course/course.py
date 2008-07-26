from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage

from models import *

from ajaxlist import get_list_context, filter_objects

from string import atoi

def find_course(request):
    list_context = get_list_context(request, default_sort = "department_abbr", default_max = "20")
    query_function = lambda objects, query: Course.objects.ft_query(query, objects = objects)
    temp = filter_objects(Course, list_context, query_objects = query_function)
    courses = None
    if temp:
        (courses, pages) = temp
    return render_to_response("course/ajax/find_course.html", {"courses" : courses}, context_instance = RequestContext(request))
    
def course_autocomplete(request):
    def iter_results(courses):
        if courses:
            for r in courses:
                yield '%s|%s\n' % (r.short_name(space = True), r.id)
    
    if not request.GET.get('q'):
        return HttpResponse(mimetype='text/plain')
    
    q = request.GET.get('q')
    limit = request.GET.get('limit', 15)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    courses = Course.objects.ft_query(q)[:limit]
    return HttpResponse(iter_results(courses), mimetype='text/plain')
