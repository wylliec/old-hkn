from hkn.exam.models import *
from hkn.exam.forms import *
from hkn.course.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
import math

def split_list(li, splits):
    last_index = 0
    li_lists = []
    for i in range(splits):
        ind = int(math.ceil(((i+1.0)*len(li))/splits))
        li_lists.append(li[last_index:ind])
        last_index = ind
    return li_lists

def main(request):
    return render_to_response("exam/main.html", context_instance=RequestContext(request))

def faq(request):
    return render_to_response("exam/faq.html", context_instance=RequestContext(request))

def committee(request):
    return render_to_response("exam/committee.html", context_instance=RequestContext(request))

def onlineexams(request):
    return render_to_response("exam/onlineexams.html", context_instance=RequestContext(request))

def browse(request):
    departments = list(Department.objects.order_by("name"))
    departments = [d for d in departments if len(d.course_set.all()) > 20]
    dept_lists = split_list(departments, 3)

    d = {"dept_lists" : dept_lists}
    return render_to_response("exam/browse.html", d, context_instance=RequestContext(request))

def browse_department(request, department_abbr):
    department = get_object_or_404(Department, abbr__iexact = department_abbr)
    courses = list(department.course_set.order_by("id"))
    courses_lists = split_list(courses, 3)

    d = {"courses_lists" : courses_lists, "department" : department}
    return render_to_response("exam/browse_department.html", d, context_instance=RequestContext(request))
