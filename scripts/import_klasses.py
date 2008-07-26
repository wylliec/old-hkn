#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, datetime, pdb
from string import atoi
from xml.dom import minidom

import sys
sys.path.append("course")
from constants import DEFAULT_DEPARTMENTS
sys.path.remove("course")

import hkn_settings

from course.models import *
from course.constants import EXAMS_PREFERENCE

#bad_klasses = ( "MEC ENG-297--Summer-2008", "INTEGBI-116-SAKANARI, J A-Summer-2008", "INTEGBI-141-NIERMANN, G L-Summer-2008", "MCELLBI-63-REYES, J A-Summer-2008" )

def normalize_dept(abbr):
    dept_replace = {"BUS ADM" : "UGBA"}
    return dept_replace.get(abbr, abbr)

instructor_patterns = (
                         re.compile(r'(?P<last>\w*),\s*(?P<first>\w*)'),                      # matches "Harvey, B"
                         re.compile(r'(?P<last>\w*),\s*(?P<first>\w)\s*(?P<middle>\w)'),                      # matches "Harvey, B H"
                         )

def safe_title(fun):
    def st(e):
        if e:
            return e.title()
        return ""
    def do_it(*args, **kwargs):
        return map(lambda e: st(e), fun(*args, **kwargs))
    return do_it

@safe_title                         
def parse_name(name):
    for instructor_pattern in Instructor.QuerySet.instructor_patterns:
        m = instructor_pattern.match(name)
        if m:
            d = m.groupdict()
            return (d.get("first"), d.get("middle"), d.get("last"))
    return ("", "", "")

def createInstructor(dpt, name):
    if name == "THE STAFF":
        return None
    first, middle, last = parse_name(name)
    
    inst = Instructor(department = dpt, first = first, middle = middle, last = last, email = "", distinguished_teacher = False, exams_preference = EXAMS_PREFERENCE.UNKNOWN)
    inst.save()
    return inst
    
                             
def getInstructor(dpt, name):
    (first, middle, last) = parse_name(name)

    objects = Instructor.objects.filter(last__iexact = last)
    if len(objects) == 1:
        return objects[0]
    elif len(objects) == 0:
        raise Instructor.DoesNotExist, "could not find instructor with last name!"

    if first:
        objects = objects.filter(first__istartswith = first)
        if len(objects) == 1:
            return objects[0]
        elif len(objects) == 0:
            raise Instructor.DoesNotExist, "could not find instructor with last and first name!"
    
    objects = objects.filter(department = dpt)
    if len(objects) == 1:
        return objects[0]
    elif len(objects) == 0:
        raise Instructor.DoesNotExist, "could not find instructor with lastname, firstname, and department!"
    
    if middle:
        objects = objects.filter(middle__istartswith = middle)
    if len(objects) == 1:
        return objects[0]
    elif len(objects) == 0:
        raise Instructor.DoesNotExist, "could not find instructor with lastname, firstname, department, and middlename!"

    raise Instructor.DoesNotExist, "too many after all filters! " + str(objects)
    
def getCourse(dpt, number, endswith = False):
    if not endswith:
        return Course.objects.get(department = dpt, number=number)
    else:
        return Course.objects.get(department = dpt, number__iendswith =number)


def getSeason(season):
    return Season.objects.get(name__iexact = season)    

def importKlass(dpt, klass, year, season):
    name = klass.getAttribute("name")
    number = klass.getAttribute("course_number")[1:].strip()
    units = klass.getAttribute("units")
    section = klass.getAttribute("section")
    (section, section_type) = section.strip().split(" ")
    instructor = klass.getAttribute("instructor")

    if len(klass.childNodes) > 0:
        section_note = klass.getElementsByTagName("note")[0].firstChild.data
    else:
        section_note = ""

    try:
        ssn = getSeason(season)
        yr = datetime.date(month=1, day=1, year=atoi(year))

        if ssn.name == "summer" and number[0] == "N":
            number = number[1:]
            try:
                course = getCourse(dpt, number)
            except Exception, e:
                course = getCourse(dpt, number, endswith = True)
        else:
            course = getCourse(dpt, number)
    except Course.DoesNotExist, e:
        course = Course(department=dpt, number=number, name=name, description="")
        course.save()
        #print "COURSE: created %s: '%s' '%s'" % (str(course), dpt.abbr, number)
    except Exception, e:
        tpls = "%s-%s-%s-%s-%s" % (dpt.abbr, number, instructor, season, year)
        #print "Couldn't match: " + tpls
        #if tpls not in bad_klasses:
        #    raise e
        #else:
        return


    try:
        kls = Klass.objects.get(course = course, season = ssn, year = yr, section = section)
    except Klass.DoesNotExist:
        kls = Klass(course = course, season = ssn, year = yr, section = section, section_type = section_type)
    kls.section_note = section_note

    kls.save()

    try:
        if len(instructor.strip()) > 0:
            inst = getInstructor(dpt, instructor)
        else:
            inst = None
    except Instructor.DoesNotExist:
        #print "Could not find instructor: " + instructor
        inst = createInstructor(dpt, instructor)
        

    if inst:
        if inst not in kls.instructor_set.all():
            kls.instructor_set.add(inst)


def importDepartment(department, year, season):
    abbr = department.getAttribute('abbr')    
    try:
        dpt = Department.objects.get(abbr__iexact = normalize_dept(abbr.upper()))
    except Department.DoesNotExist:
        raise Exception, "Couldn't find department with abbreviation %s and can't create (don't know full name)!" % (abbr, )
    
    for klass in department.getElementsByTagName("klass"):
        if klass.hasAttribute("course_number") and klass.getAttribute("course_number")[0] == "P":
            importKlass(dpt, klass, year, season)

def importSemester(semester):
    year = semester.getAttribute("year")
    season = semester.getAttribute("season")
    for department in semester.getElementsByTagName("department"):
        if department.getAttribute("abbr").lower() in DEFAULT_DEPARTMENTS:
            importDepartment(department, year, season)

def importFromXmlFile(klassFile):
    dom = minidom.parse(file(klassFile, "r"))
    for semester in dom.getElementsByTagName("semester"):
        importSemester(semester)
        
def main():
#    klassFiles = glob.glob("klass/xml/*.xml")
    klassFiles = glob.glob("klass/xml/*2007*.xml")
    klassFiles += glob.glob("klass/xml/*2008*.xml")
    for klassFile in klassFiles:
        print "Importing klasses from " + klassFile
        importFromXmlFile(klassFile)

if __name__ == "__main__":
    main()

