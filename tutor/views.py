# tutoring views
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django import forms
from string import atoi

from django.contrib.auth.decorators import *

from course.models import Department
from hkn.tutor import models as tutor
from hkn.info import models as hknmodels

from nice_types import NiceDict
from nice_types import NamedList
from nice_types import QueryDictWrapper

from hkn.tutor.constants import *
from hkn.tutor.scheduler import State, Slot
from hkn.tutor import output
from hkn.info import infobox
import nice_types.semester

from re import match, search

#helper methods
def basicContext(request, info = {}):
    ret = NiceDict(False, info)
    if request.user.is_authenticated:
        ret['user'] = request.user
    return ret

class NoTutorSchedulesException(Exception):
    pass

def get_max_version():
    try:
        return max(tutor.Assignment.objects.values_list('version'))[0]
    except ValueError:
        raise NoTutorSchedulesException("There are no tutoring schedules available")
    
def get_published_version():
    try:
        return int(HKN.objects.get("hkn_tutor_version").value)
    except:
        return get_max_version()
        
def get_published_assignments(version=None):
    try:
        if not version:
            version = get_published_version()
        assignments = tutor.Assignment.objects.filter(version=version).select_related('person')
        if len(assignments) == 0:
            return None    
        return assignments
    except NoTutorSchedulesException:
        return None



def get_tutor_info(tutoring_days=TUTORING_DAYS, tutoring_times=TUTORING_TIMES):
    assignments = get_published_assignments().select_related("person__user")
    
    realAssignments = {} #dictionary from slot to person object
    for assignment in assignments:
        slot = Slot(tutor.get_day_from_slot(assignment.slot),
                    tutor.get_time_from_slot(assignment.slot),
                    assignment.office)
        if slot in realAssignments:
            realAssignments[slot].append(assignment.person)
        else:
            realAssignments[slot] = [assignment.person]

    canTutorData = tutor.CanTutor.objects.for_current_semester().select_related('course')
           
    tutors = {}
    """ person -> courses """
    
    schedule = []
    
    for time in tutoring_times:    
        time_schedule = NamedList(time)
        schedule.append(time_schedule)        
        for day in tutoring_days:
            day_schedule = {}
            time_schedule.append(day_schedule)
            for office in (CORY, SODA):
                slot_schedule = {}
                day_schedule[office] = slot_schedule
                
                slot = Slot(day, time, office)
                slot_schedule["slot"] = slot
                slot_schedule["people"] = []
                
                people = realAssignments[slot]
                for person in people:
                    if person not in tutors.keys():
                        cantutors = person.cantutor_set.select_related('course')
                        tutors[person] = " ".join([x.course.short_name() + (x.current and "cur" or "") for x in cantutors])
                    slot_schedule["people"].append((person, tutors[person]))
    
    tutors = tutors.keys()
    return schedule, canTutorData.filter(person__in = tutors), tutors

def get_courses_tutored(can_tutor):
    canTutor = {} #dictionary of dept -> list of courses
    for x in can_tutor:
        course = x.course
        abbr = Department.get_nice_abbr(course.department_abbr)
        if abbr not in canTutor:
            canTutor[abbr] = []
        if course.number not in canTutor[abbr]:
            canTutor[abbr].append(course.coursenumber)

    def courseSort(x, y):
        nx = int(search("\d+", x).group(0))
        ny = int(search("\d+", y).group(0))
        r = cmp(nx, ny)
        if r == 0:
            return cmp(x, y)
        return r

    sortedCanTutor = canTutor.items()
    for department, courses in sortedCanTutor:
        courses.sort(courseSort)    
    return sortedCanTutor

def schedule(request):
    context = basicContext(request)
    context['days'] = TUTORING_DAYS
    context['timeslots'] = TUTORING_TIMES
    context['message'] = False
    context['year'] = nice_types.semester.current_year()
    context['season'] = nice_types.semester.current_semester().season_name.title()
    
    assignments = get_published_assignments(request.GET.get('version', None))
    
    if not assignments:
        context['message'] = 'Tutoring schedule not available.'
        return render_to_response('tutor/schedule.html',
                                  context,
                                  context_instance = RequestContext(request))
                                      
    schedule, can_tutor, tutors = get_tutor_info()
    can_tutor = get_courses_tutored(can_tutor)

    context['schedule'] = schedule
    context['can_tutor'] = can_tutor
    context['header'] = {"cory" : "Cory Office (290 Cory Hall) Schedule", "soda" : "Soda Office (345 Soda Hall) Schedule"}
    context['infoboxes'] = infobox.tutors(request, tutors)

    return render_to_response('tutor/schedule.html',
                              context,
                              context_instance = RequestContext(request))

# vim: set expandtab softtabstop=4 tabstop=4 shiftwidth=4: