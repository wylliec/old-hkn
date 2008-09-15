from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import math

from course.models import *
from models import *
from forms import *

from ajaxlist.helpers import render_ajaxlist_response, get_ajaxinfo, sort_objects, paginate_objects


try:
	from settings import EXAM_LOGIN_REQUIRED
except: 
	EXAM_LOGIN_REQUIRED = True


def view(request, exam_id):
	pass

def split_list(li, splits):
	last_index = 0
	li_lists = []
	for i in range(splits):
		ind = int(math.ceil(((i+1.0)*len(li))/splits))
		li_lists.append(li[last_index:ind])
		last_index = ind
	return li_lists

def browse(request):
	courses = Course.objects.filter(exam__publishable=True).select_related('department').annotate_exam_count(True).order_by("published_exam_count")
	departments = Department.objects.filter(exam__isnull=False).distinct().order_by("name")
	#departments = list(Department.objects.order_by("name"))
	#departments = [d for d in departments if d.course_set.count() > 20 and d.exam_set.count() > 0]

	d = {"departments" : departments}
	return render_to_response("exam/browse.html", d, context_instance=RequestContext(request))

def browse_department(request, department_abbr):
	department = get_object_or_404(Department, abbr__iexact = department_abbr)
	#courses = list(department.course_set.order_by("id"))
	courses = department.course_set

	if not request.user.has_perm("exam.add_exam"):
		#courses = filter(lambda c: c.exam_set.filter(publishable=True).count() > 0, courses)
		courses = courses.filter(exam__publishable=True).distinct()
		#for c in courses.iterator():
		#	c.exam_count = c.exam_set.filter(publishable=True).count()
	else:
		#courses = filter(lambda c: c.exam_set.count() > 0, courses)
		courses = courses.filter(exam__isnull=False).distinct()
		#for c in courses.iterator():
		#	c.exam_count = "%d, %d" % (c.exam_set.filter(publishable=True).count(), c.exam_set.filter(publishable=False).count())

	empty = courses.count() == 0
	courses_lists = split_list(courses, 2)
	d = {"courses_lists" : courses_lists, "department" : department, "empty" : empty}
	return render_to_response("exam/browse_department.html", d, context_instance=RequestContext(request))    

def exam_autocomplete(request):
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

	courses = filter(lambda x: x.published_exam_count > 0, Course.objects.ft_query(q).annotate_exam_count())[:limit]
	return HttpResponse(iter_results(courses), mimetype='text/plain')

if EXAM_LOGIN_REQUIRED:
	browse = login_required(browse)
	browse_department = login_required(browse_department)
