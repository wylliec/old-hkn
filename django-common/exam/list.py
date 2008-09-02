from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, render_ajaxlist_response
from course.models import *
from string import atoi

from constants import FILE_UPLOAD_DIR, EXAM_TYPE
from models import Exam


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
	objects = objects.filter(exam_type__in=(EXAM_TYPE.MIDTERM, EXAM_TYPE.FINAL))
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
	return objects.distinct()


def get_new_dict():
	default_dict = SortedDict()
	default_dict["Midterm 1"] = []
	default_dict["Midterm 2"] = []
	default_dict["Midterm 3"] = []
	default_dict["Final"] = []
	return default_dict
def regroup_exams(course_id, exams):
	exams = exams.filter(course=course_id).order_by('-klass__semester', 'exam_type', 'number').select_related('klass')
	d = SortedDict()
	
	for e in exams:
		k1 = e.klass
		k2 = e.describe_exam_type()
		if d.has_key(k1):
			if d[k1].has_key(k2):
				d[k1][k2].append(e)
			else:
				d[k1][k2] = [e]
		else:
			d[k1] = get_new_dict()
			d[k1][k2] = [e]
	return d


def get_exams_dict(filters, view_unpublished=False):
	all_exams = Exam.published.all()
	if view_unpublished:
		all_exams = Exam.all.all()
	
	exams = filter_exams(all_exams, filters)
	exams_dict = {}

	if len(exams) > 0:
		exams_courses = exams.select_related('course', 'klass').order_by('id').values('course').distinct()[:5]

		course_ids = set([c["course"] for c in exams_courses])
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
