#!/usr/bin/env python
import setup_settings
from course.models import *

CURRENT_LEVEL = 0
def debug(msg, level=10):
    if level > CURRENT_LEVEL:
        print msg

def get_instructor(course, instructor_name):
    eecs_departments = Department.objects.filter(abbr__in = ("COMPSCI", "EL ENG"))
    instructor = Instructor.objects.ft_query(instructor_name).filter(departments__in = eecs_departments)
    if len(instructor) == 1:
        return instructor[0]
    if len(instructor) == 0:
        raise Exception("Found no instructors %s in EECS! Returning the first one" % instructor_name)
    if len(instructor) > 1:
        debug("Found multiple instructors %s in EECS! Returning the first one" % instructor_name)
        return instructor[0]

def get_klass(dept, course, instructor, season, year):
    """ all args should be strings """
    season = Season.objects.get_cached(name=season)
    year = datetime.date(int(year), 1, 1)
    course = Course.objects.query_exact(dept, course)
    if len(course) != 1:
        raise Exception("bad number of courses! %s" % course)
    course = course[0]
    
    instructor = get_instructor(course, instructor)
    debug("Working on klass %s %s %s %s" % (course, instructor.short_name(True, True), season, year))
    klasses = Klass.objects.filter(year=year, season=season, course=course)
    if len(klasses) == 0:
        klass = Klass(course=course, season=season, year=year, section_type="LEC", section="", section_note="")
        klass.save()
        klass.instructors.add(instructor)
        return klass
    elif len(klasses) == 1:
        klass = klasses[0]
        if instructor in klass.instructors.all():
            return klass
        debug("Found only 1 klass but instructor mismatch! %s not in %s" % (instructor, klass.instructors.all()))
        klass.instructors.add(instructor)
        return klass
    else:
        klasses2 = klasses.filter(instructors = instructor)
        if len(klasses2) == 1:
            return klasses2[0]
        elif len(klasses2) > 1:
            raise Exception("Found 2 klasses with an instructor in the same semester! ids: %s" % klasses2.values_list('id', flat=True))
        raise Exception("Multiple klasses for the semester, but none with the right instructor! What to do? klasses %s" % (klasses.values_list('id', flat=True)))
        

if __name__ == "__main__":
    import sys
    get_klass(*sys.argv[1:])
