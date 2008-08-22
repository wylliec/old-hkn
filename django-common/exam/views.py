from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
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
	departments = list(Department.objects.order_by("name"))
	departments = [d for d in departments if d.course_set.count() > 20 and d.exam_set.count() > 0]
	dept_lists = split_list(departments, 2)

	d = {"dept_lists" : dept_lists}
	return render_to_response("exam/browse.html", d, context_instance=RequestContext(request))

def browse_department(request, department_abbr):
	department = get_object_or_404(Department, abbr__iexact = department_abbr)
	courses = list(department.course_set.order_by("id"))

	if not request.user.has_perm("exam.add_exam"):
		courses = filter(lambda c: c.exam_set.filter(publishable=True).count() > 0, courses)
		for c in courses:
			c.exam_count = c.exam_set.filter(publishable=True).count()
	else:
		courses = filter(lambda c: c.exam_set.count() > 0, courses)
		for c in courses:
			c.exam_count = "%d, %d" % (c.exam_set.filter(publishable=True).count(), c.exam_set.filter(publishable=False).count())

	empty = len(courses) == 0
	courses_lists = split_list(courses, 2)
	d = {"courses_lists" : courses_lists, "department" : department, "empty" : empty}
	return render_to_response("exam/browse_department.html", d, context_instance=RequestContext(request))    

if EXAM_LOGIN_REQUIRED:
	browse = login_required(browse)
	browse_department = login_required(browse_department)
