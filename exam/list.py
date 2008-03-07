from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from hkn.list import get_list_context, filter_objects
from hkn.exam.models import *
from hkn.course.models import *
from string import atoi

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

    return "%s|%s|%s" % (courses_string, types_string, numbers_string)
           

def list_exams(request, course = None, exam_type = None):
    category = get_category_string(courses = [course], exam_types = [exam_type])
    d = get_list_context(request, default_sort = "-exam_date", default_category = category, default_max = "100")    
    d["objects_url"] = urlresolvers.reverse("hkn.exam.list.list_exams_ajax")
    #d["extra_javascript"] = "event/ajax/list_events_javascript.html"
    return render_to_response("list/list.html", d, context_instance=RequestContext(request))

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
    
    if objects == None:
        objects = Exam.objects.all()
        
    if len(categories) == 0:
        return objects
    
    for category_type in CATEGORY_FILTERS.keys():
        values = [c[len(category_type)+1:] for c in categories if c.startswith(category_type)]
        if len(values) == 0:
            continue
        objects = filter_exams_with_function(objects, values, CATEGORY_FILTERS[category_type])    
    return objects

def list_exams_ajax(request):
    list_context = get_list_context(request, default_sort = "-exam_date", default_max = "100")
    
    exams = get_exams_for_categories(list_context["categories"])
    exams_courses = exams.order_by('course_id').values('course').distinct()[:5]

    course_ids = [c["course"] for c in exams_courses]
    exams = get_exams_for_categories(list_context["categories"], Exam.objects.filter(course__in = course_ids)).order_by('course_id', 'exam_type', 'number')
    
    exams_dict = {}
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
    
    return render_to_response("exam/ajax/list_exams.html", list_context, context_instance = RequestContext(request))