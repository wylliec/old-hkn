#!/usr/bin/env python
import setup_settings
from course.models import *
import types

CURRENT_LEVEL = 11
def debug(msg, level=10):
    if level > CURRENT_LEVEL:
        print msg

class MissingCourseException(Exception):
	pass

class MissingInstructorException(Exception):
	pass

class ManyInstructorsInDepartment(Exception):
    pass

class KlassesException(Exception):
    pass

class NoKlasses(KlassesException):
    pass

class InstructorMismatch(KlassesException):
    pass

class ManyKlassesInstructorMismatch(KlassesException):
    pass

class InstructorManyKlasses(KlassesException):
    pass

def instructor_string(instructors):
    return ", ".join([i.short_name(True, True) for i in instructors])

def get_instructor(instructor_name, dept_abbrs=[]):
    departments = Department.objects.filter(abbr__in = dept_abbrs)
    instructor = Instructor.objects.ft_query(instructor_name).filter(departments__in = departments)
    if len(instructor) == 1:
        return instructor[0]
    if len(instructor) > 1:
        debug("Found multiple instructors %s in departments! Returning the first of %s" % (instructor_name, instructor_string(instructor)))
        return instructor[0]
    raise MissingInstructorException("Found no instructors %s in departments %s!" % (instructor_name, dept_abbrs))
    instructor = Instructors.objects.ft_query(instructor_name)
    if len(instructor) == 1:
        return instructor[0]
    if len(instructor) > 1:
        debug("No instructor %s in departments %s, but multiple in general! Returning the first one" % instructor_name, dept_abbrs)
        return instructor[0]
    raise MissingInstructorException("No instructors %s at all!" % instructor_name)
    
def get_instructor_safe(*args, **kwargs):
    try:
        return get_instructor(*args, **kwargs)
    except MissingInstructorException:
        return Instructor.objects.get(first="Null", last="Instructor")

def get_klass(dept, course, instructors, season=None, year=None, semester=None):
    """ all args should be strings """
    if not semester:
        semester = Semester(season_name=season, year=year)
    elif semester and type(semester) in types.StringTypes:
        semester = Semester.for_semester(semester)

    course = Course.objects.query_exact(dept, course)
    if len(course) != 1:
        course = Course.objects.query_exact(dept, course, number=True)
        if len(course) != 1:
            raise MissingCourseException("bad number of courses! %s" % course)
    course = course[0]
    
    instructors = [get_instructor_safe(i, [course.department_abbr]) for i in instructors]
    debug("Working on klass %s %s %s" % (course, instructor_string(instructors), semester))
    return (get_klass_helper(course, instructors, semester), instructors)

def get_klass_helper(course, instructors, semester):
    klasses = Klass.objects.filter(course=course, semester=semester)
    instructors_set = set(instructors)
    if len(klasses) == 1:
        klass = klasses[0]
        if klass.instructors.count() == 0 or len(instructors_set & set(klass.instructors.all())) != 0:
            return klass
        new_klass = Klass(course=course, semester=semester, section_type="LEC", section="", section_note="CREATED")
        raise InstructorMismatch("Found 1 klass but instructor mismatch!", klass, instructors, new_klass)
    elif len(klasses) == 0:
        klass = Klass(course=course, semester=semester, section_type="LEC", section="", section_note="CREATED")
        raise NoKlasses("No matching klasses!", klass, instructors)
    else:
        klasses2 = klasses.filter(instructors__in = instructors)
        if len(klasses2) == 1:
            return klasses2[0]
        elif len(klasses2) > 1:
            raise InstructorManyKlasses("Found >1 klasses with an instructor in the same semester!", klasses2, instructors)
        raise ManyKlassesInstructorMismatch("Multiple klasses for the semester, but none with the right instructor! What to do?", klasses, instructors)
        

if __name__ == "__main__":
    import sys
    get_klass(*sys.argv[1:])
