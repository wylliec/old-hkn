from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, render_ajaxlist_response
from course.models import *
from string import atoi

from exam.models import *


try:
    from settings import EXAM_LOGIN_REQUIRED
except:
    EXAM_LOGIN_REQUIRED = True



_EXAM_FILTER_FUNCTIONS = {
                    "exam_course" : lambda objects, value: objects.query_course(value),
                    "exam_instructor" : lambda objects, value: objects.query_instructor(value),
                    "exam_type" : lambda objects, value: objects.filter(exam_type__iexact = value),
                    "exam_number" : lambda objects, value: objects.filter(number = value),
                    "exam_after": lambda objects, value: objects.after(value),
                    }

def filter_exams(objects, filters):
    if len(filters) == 0:
        return Exam.published.none()
    
    for filter_type in _EXAM_FILTER_FUNCTIONS.keys():
        if not filters.has_key(filter_type):
            continue
        values = [filters[filter_type]]
        filter_function = _EXAM_FILTER_FUNCTIONS[filter_type]
        filtered_objects = Exam.published.none()
        for value in values:
            filtered_objects = filtered_objects | filter_function(objects, value)
        objects = filtered_objects
    return objects
    
EXAM_TYPE_NUM = {EXAM_TYPE.FINAL: 20, EXAM_TYPE.MIDTERM: 15, EXAM_TYPE.REVIEW: 10, EXAM_TYPE.QUIZ: 5}
EXAM_NUM_TYPE = {20: EXAM_TYPE.FINAL, 15:EXAM_TYPE.MIDTERM, 10:EXAM_TYPE.REVIEW, 5: EXAM_TYPE.QUIZ}
def regroup_exams(course_id, exams):
    regroup_dict = {}
    key_for_exam = lambda e: (EXAM_TYPE_NUM[e.exam_type], e.number)
    describe_key = lambda k: "%s %s" % (EXAM_TYPE[EXAM_NUM_TYPE[k[0]]], (k[0] != EXAM_TYPE.FINAL) and str(k[1]) or " ")
    exams = list(exams.filter(course=course_id))
#    exams.sort(lambda e1, e2: cmp(e2.get_semester_sort(), e1.get_semester_sort()))
    for e in exams:
        k = key_for_exam(e)
        if regroup_dict.has_key(k):
            regroup_dict[k].append(e)
        else:
            regroup_dict[k] = [e]
            
    keys = regroup_dict.keys()
    keys.sort()
    return [(describe_key(k), regroup_dict[k]) for k in keys]

def get_exams_dict(filters, view_unpublished=False):
    all_exams = Exam.published.all()
    if view_unpublished:
        all_exams = Exam.all.all()
    
    exams = filter_exams(all_exams, filters)
    exams_dict = {}

    if len(exams) > 0:
        exams_courses = exams.select_related('course', 'klass').order_by('id').values('course').distinct()[:5]

        course_ids = [c["course"] for c in exams_courses]
        exams = filter_exams(all_exams.filter(course__in = course_ids), filters).order_by('-exam_date')
    
        for course_id in course_ids:
            c = Course.objects.get(pk=course_id)
            exams_dict[c] = regroup_exams(course_id, exams)
    
    return exams_dict

def list_exams(request):
    d = get_ajaxinfo(request.GET)
    
    view_unpublished = False
    if request.user.has_perm('exam.add_exam'):
        view_unpublished = True
    d['view_unpublished'] = view_unpublished
    
    exam_filters = dict((k, v) for k, v in request.GET.items() if k.startswith("exam_") and len(v) > 0)    
    d['exams_dict'] = get_exams_dict(exam_filters, view_unpublished=view_unpublished)
    d.update(exam_filters)

    return render_ajaxlist_response(request.is_ajax(), "exam/list_exams.html", d, context_instance=RequestContext(request))


if EXAM_LOGIN_REQUIRED:
    list_exams = login_required(list_exams)
