from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required

from ajaxlist import get_list_context, filter_objects
from course.models import *
from string import atoi

from models import *

try:
    from settings import EXAM_LOGIN_REQUIRED
except:
    EXAM_LOGIN_REQUIRED = True

def get_category_string(courses = None, exam_types = None, exam_numbers = None):
    courses_string = types_string = numbers_string = ""
    
    if courses:
        courses = [c for c in courses if c is not None]
        if len(courses) > 0:
            courses_string = "course:" + "|course:".join(courses)

    if exam_types:
        exam_types = [c for c in exam_types if c is not None]    
        if len(exam_types) > 0:
            types_string = "type:" + "|type:".join(exam_types)
            
    if exam_numbers:
        exam_numbers = [c for c in exam_numbers if c is not None]    
        if len(exam_numbers) > 0:
            numbers_string = "number:" + "|number:".join(exam_numbers)

    return "|".join([st for st in [courses_string, types_string, numbers_string] if len(st) > 0])
           

CATEGORY_FILTERS = {"course" : lambda objects, value: Exam.objects.query_course(value, objects),
                    "instructor" : lambda objects, value: Exam.objects.query_instructor(value, objects),
                    "type" : lambda objects, value: objects.filter(exam_type__iexact = value),
                    "number" : lambda objects, value: objects.filter(number = value),
                    }

def get_exams_for_categories(categories, objects = None):
    def filter_exams_with_function(objects, values, object_filter):
        return_objects = Exam.objects.none()
        for value in values:
            return_objects = return_objects | object_filter(objects, value)
        return return_objects

    if len(categories) == 0:
        return Exam.objects.none()
    
    if objects == None:
        objects = Exam.objects.all()
        
    
    for category_type in CATEGORY_FILTERS.keys():
        values = [c[len(category_type)+1:] for c in categories if c.startswith(category_type)]
        if len(values) == 0:
            continue
        objects = filter_exams_with_function(objects, values, CATEGORY_FILTERS[category_type])    
    return objects

def get_list_exams_context(request, category = None):
    list_context = get_list_context(request, default_sort = "-exam_date", default_max = "100", default_category=category)
    exams = get_exams_for_categories(list_context["categories"])
    exams_dict = {}

    if len(exams) > 0:
        exams_courses = exams.order_by('course_id').values('course').distinct()[:5]

        course_ids = [c["course"] for c in exams_courses]
        exams = get_exams_for_categories(list_context["categories"], Exam.objects.filter(course__in = course_ids)).order_by('course_id', 'exam_type', 'number')
    
        for course_id in course_ids:
            c = Course.objects.get(pk = course_id)
            exams_for_course = [e for e in exams if e.course_id == course_id]
            exams_dict[c] = exams_for_course
    
    list_context["exams"] = exams
    list_context["exams_dict"] = exams_dict
    
    for category_type in CATEGORY_FILTERS.keys():
        values = [c[len(category_type)+1:] for c in list_context["categories"] if c.startswith(category_type)]
        if len(values) == 0:
            continue
        list_context[category_type + "_filter"] = values[0]    


    return list_context


def list_exams(request, course = None, exam_type = None):
    category = get_category_string(courses = [course], exam_types = [exam_type])
    list_context = get_list_exams_context(request, category)
    list_context["objects_url"] = urlresolvers.reverse("exam.list.list_exams_ajax")
    list_context["parent_template"] = "exam/search.html"
    list_context["view_template"] = "exam/ajax/_list_exams.html"
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance=RequestContext(request))

def list_exams_ajax(request):
    list_context = get_list_exams_context(request)
    return render_to_response("exam/ajax/_list_exams.html", list_context, context_instance = RequestContext(request))

if EXAM_LOGIN_REQUIRED:
    list_exams_ajax = login_required(list_exams_ajax)
    list_exams = login_required(list_exams)
