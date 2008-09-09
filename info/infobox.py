from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.cache import cache
from hkn.info.models import Person
from hkn.tutor.models import get_time_from_slot, get_day_from_slot, make_slot
from hkn.tutor.constants import TUTORING_DAYS, TUTORING_TIMES

def tutors(request, people):
	d = {}
	tutors = []
	for person in people:
		cache_key = 'tutor_infobox_%d' % person.id
		tutor_infobox = cache.get(cache_key)
		if not tutor_infobox:
			courses_tutored = ", ".join([ct.course.short_name() for ct in person.cantutor_set.for_current_semester().select_related("course").order_by('course__department_abbr', 'course__integer_number')])
			d["person"] = person
			d["assignments"] = merge_assignments((list(person.assignment_set.for_current_semester().latest_version())))
			d["courses"] = courses_tutored
			tutor_infobox = render_to_string("info/infobox/tutor.html", d)
			cache.set(cache_key, tutor_infobox, 600)
		tutors.append(tutor_infobox)
	return "".join(tutors)

def sort_assignments(assignments):
	def assignmentSort(x, y):
		day1 = get_day_from_slot(x.slot)
		day2 = get_day_from_slot(y.slot)
		if day1 == day2:
			slot1 = get_time_from_slot(x.slot)
			slot2 = get_time_from_slot(y.slot)
			return list(TUTORING_TIMES).index(slot1) - list(TUTORING_TIMES).index(slot2)
		return list(TUTORING_DAYS).index(day1) - list(TUTORING_DAYS).index(day2)

	return assignments.sort(cmp=assignmentSort)

def merge_assignments(assignments):
	if len(assignments) <= 1:
		return assignments

	day1 = get_day_from_slot(assignments[0].slot)
	day2 = get_day_from_slot(assignments[1].slot)
	if day1 == day2:
		slot_pair1 = get_time_from_slot(assignments[0].slot).split('-')
		slot_pair2 = get_time_from_slot(assignments[1].slot).split('-')
		if slot_pair1[1] == slot_pair2[0]:
			assignments[0].slot = make_slot(get_day_from_slot(assignments[0].slot), "-".join([slot_pair1[0] , slot_pair2[1]]))
			return merge_assignments(assignments[:1] + assignments[2:])
	return assignments[:1] + merge_assignments(assignments[1:])
