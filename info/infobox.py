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
            courses_completed = []
            courses_current = []
            for ct in person.cantutor_set.for_current_semester().select_related("course").order_by('course__department_abbr', 'course__integer_number'):
                if ct.current:
                    courses_current.append(ct.course.short_name())
                else:
                    courses_completed.append(ct.course.short_name())
            d["person"] = person
            d["assignments"] = merge_assignments(sort_assignments(list(person.assignment_set.for_current_semester().latest_version())))
            if len(courses_current) > 0:
                d["courses_current"] = ", ".join(courses_current)
            else:
                d["courses_current"] = None
            d["courses_completed"] = ", ".join(courses_completed)
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

    assignments.sort(cmp=assignmentSort)
    return assignments

def merge_assignments(assignments):
    if assignments is None or len(assignments) <= 1:
        return assignments

    day1 = get_day_from_slot(assignments[0].slot)
    day2 = get_day_from_slot(assignments[1].slot)
    if day1 == day2 and assignments[0].office == assignments[1].office:
        slot_pair1 = get_time_from_slot(assignments[0].slot).split('-')
        slot_pair2 = get_time_from_slot(assignments[1].slot).split('-')
        if slot_pair1[1] == slot_pair2[0]:
            assignments[0].slot = make_slot(get_day_from_slot(assignments[0].slot), "-".join([slot_pair1[0] , slot_pair2[1]]))
            return merge_assignments(assignments[:1] + assignments[2:])
    return assignments[:1] + merge_assignments(assignments[1:])
