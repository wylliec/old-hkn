# tutoring views
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.conf import settings
from django.core.cache import cache

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
from hkn.main.property import PROPERTIES
import nice_types.semester

from re import match, search

#helper methods
def basicContext(request, info = {}):
    ret = NiceDict(False, info)
    if request.user.is_authenticated:
        ret['user'] = request.user
    return ret

class NoTutorScheduleException(Exception):
    pass

def get_max_version():
    try:
        return max(tutor.Assignment.objects.values_list('version'))[0]
    except ValueError:
        raise NoTutorScheduleException("There are no tutoring schedules available")
    
def get_published_version():
    try:
        return int(PROPERTIES.hkn_tutor_version)
    except Exception, e:
        #if getattr(settings, 'DEBUG', False):
        #    return get_max_version()
        #else:
        raise NoTutorScheduleException("There is no published tutoring schedule")
        
def get_published_assignments(version=None):
    """ Might throw NoTutorScheduleException """
    if not version:
        version = get_published_version()
    assignments = tutor.Assignment.objects.for_current_semester().filter(version=version).select_related('person')
    if len(assignments) == 0:
        raise NoTutorScheduleException("There is no published tutoring schedule")
    return assignments


def get_tutor_info(tutoring_days=TUTORING_DAYS, tutoring_times=TUTORING_TIMES):
    canTutorData = tutor.CanTutor.objects.for_current_semester().select_related('course')    
    
    tutor_info_cache_key= 'tutor_info_%d' % hash(tuple(tutoring_days))
    if cache.has_key(tutor_info_cache_key):
        schedule, tutors = cache.get(tutor_info_cache_key)
        return schedule, canTutorData.filter(person__in = tutors), tutors
    
    assignments = get_published_assignments().select_related("person")
        
    
    realAssignments = {} #dictionary from slot to person object
    for assignment in assignments:
        slot = Slot(tutor.get_day_from_slot(assignment.slot),
                    tutor.get_time_from_slot(assignment.slot),
                    assignment.office)
        if slot in realAssignments:
            realAssignments[slot].append(assignment.person)
        else:
            realAssignments[slot] = [assignment.person]
           
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
                        cache_key = "tutor_courses_classes_%d" % person.id
                        tutors[person] = cache.get(cache_key)
                        if not tutors[person]:
                            cantutors = person.cantutor_set.select_related('course').for_current_semester()
                            tutors[person] = " ".join([x.course.short_name() + (x.current and "cur" or "") for x in cantutors])
                            cache.set(cache_key, tutors[person], 6000)
                    slot_schedule["people"].append((person, tutors[person]))
    
    cache.set(tutor_info_cache_key, (schedule, tutors), 60000)    
    return schedule, canTutorData.filter(person__in = tutors), tutors

def get_courses_tutored(can_tutor):
    can_tutor = can_tutor.order_by("course__integer_number", "course__number", "course__coursenumber")
    canTutor = {} #dictionary of dept -> list of courses
    for x in can_tutor:
        course = x.course
        abbr = Department.get_nice_abbr(course.department_abbr)
        if abbr not in canTutor:
            canTutor[abbr] = []
        if course.coursenumber not in canTutor[abbr]:
            canTutor[abbr].append(course.coursenumber)

    return canTutor.items()

def schedule(request):
    context = basicContext(request)
    context['days'] = TUTORING_DAYS
    context['timeslots'] = TUTORING_TIMES
    context['message'] = False
    context['year'] = nice_types.semester.current_year()
    context['season'] = nice_types.semester.current_semester().season_name.title()
    
    version = None
    if request.user.has_perm("info.group_tutor"):
        version = request.GET.get('version', None)

    try:
        schedule, can_tutor, tutors = get_tutor_info()
        can_tutor = get_courses_tutored(can_tutor)
    except NoTutorScheduleException, e:
        context['message'] = 'Tutoring schedule is not yet available, please check back soon!'
        return render_to_response('tutor/schedule.html',
                                  context,
                                  context_instance = RequestContext(request))        

    context['schedule'] = schedule
    context['can_tutor'] = can_tutor
    context['header'] = {"cory" : "290 Cory Hall", "soda" : "345 Soda Hall"}
    context['infoboxes'] = infobox.tutors(request, tutors)

    return render_to_response('tutor/schedule.html',
                              context,
                              context_instance = RequestContext(request))

# vim: set expandtab softtabstop=4 tabstop=4 shiftwidth=4:
