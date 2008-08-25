#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, datetime, pdb
from string import atoi
from xml.dom import minidom
import os, sys, os.path

from constants import DEFAULT_DEPARTMENTS

import setup_settings
cd = setup_settings.get_scripts_directory()

from course.models import *
from course.constants import EXAMS_PREFERENCE
from nice_types.semester import Semester

#bad_klasses = ( "MEC ENG-297--Summer-2008", "INTEGBI-116-SAKANARI, J A-Summer-2008", "INTEGBI-141-NIERMANN, G L-Summer-2008", "MCELLBI-63-REYES, J A-Summer-2008" )

def normalize_dept(abbr):
    dept_replace = {"BUS ADM" : "UGBA"}
    return dept_replace.get(abbr, abbr)

instructor_patterns = (
     re.compile(r"(?P<last>[-A-Z']+( [-A-Z]+){0,4}), (?P<first>[A-Z])"),                      # matches "Harvey, B"
     re.compile(r"(?P<last>[-A-Z']+( [-A-Z]+){0,4}), (?P<first>[A-Z]) (?P<middle>[A-Z])"),                      # matches "Harvey, B H"
     re.compile(r"(?P<last>[A-Z]+(-[A-Z]+)?( [A-Z]+){0,4})"),                      # matches "PESTANA-NASCIMENTO"                         
)
                         
also_pattern = re.compile(r'Also: (?P<instr_1>[-A-Z]*, [A-Z](?: [A-Z])?)(?:; (?P<instr_2>[-A-Z]*, [A-Z](?: [A-Z])?))?(?:; (?P<instr_3>[-A-Z]*, [A-Z](?: [A-Z])?))?(?:; (?P<instr_4>[-A-Z]*, [A-Z](?: [A-Z])?))?(?:; (?P<instr_5>[-A-Z]*, [A-Z](?: [A-Z])?))?')

#cross_listed = re.compile(r"Cross-listed with( [A-Za-z ']+ C\d+[A-Z]* section \d+(?: and|[,.]))+")
cross_listed = re.compile(r"(?:with)? ([A-Za-z ']+? C\d+[A-Z]* section \d+)(?: and|[,.])")

def safe_title(fun):
    def st(e):
        if e:
            return e.strip().title()
        return ""
    def do_it(*args, **kwargs):
        return map(lambda e: st(e), fun(*args, **kwargs))
    return do_it

@safe_title                         
def parse_name(name):
    for instructor_pattern in instructor_patterns:
        m = instructor_pattern.match(name)
        if m:
            d = m.groupdict()
            return (d.get("first"), d.get("middle"), d.get("last"))
    return ("", "", "")

def create_instructor(dpt, name):
    if name == "THE STAFF":
        return None
    first, middle, last = parse_name(name)

    if len(last.strip()) == 0:
        raise Exception("Instructor %s last name could not be parsed" % name)

    inst = Instructor(home_department = dpt, first = first, middle = middle, last = last, email = "", distinguished_teacher = False, exams_preference = EXAMS_PREFERENCE.UNKNOWN)
    inst.save()
    return inst
    
                             
def get_instructor(dpt, name):
    (first, middle, last) = parse_name(name)
            
    instructors = Instructor.objects.hinted_query(last_name=last, first_name=first, force_first=True, department_abbrs=[dpt.abbr])
    
    if first == "" or last == "":
        print "BLANKS: %s -> '%s' '%s'" % (name, first, last)
    
    if len(instructors) == 0:
        raise Instructor.DoesNotExist, "could not find instructor with last name and first initial"
    elif len(instructors) == 1:
        instr = instructors[0]
        if instr.departments.filter(pk = dpt.id).count() != 0:
            # department matches
            return instr
#        if len(instr.middle) > 0 and instr.middle[0] == middle:
#            # middle initial matches
#            print "WARNING: Merging based on middle initial"
#            print "%s [%s] -> %s" % (name, dept, instr.short_name(True, True))
#            instr.departments.add(dpt)
#            return instr
#        if last in ("Whaley", "Adler"):
#            return instr
        print "WARNING: NOT MERGING %s [%s] -> %s" % (name, dpt, instr.short_name(True, True))
        raise Instructor.DoesNotExist, "found instructor with last name and first initial, but no department or middle initial match"
#    else:
#        print "Too many instructors?!"
#        import pdb; pdb.set_trace()

    raise Instructor.DoesNotExist, "too many after all filters! %s" % str(instructors)
    
def get_course(dpt, number, endswith = False):
    if not endswith:
        return Course.objects.get(department = dpt, coursenumber=number)
    else:
        return Course.objects.get(department = dpt, coursenumber__iendswith =number)


def importKlass(dpt, klass, year, season):
    name = klass.getAttribute("name")
    number = klass.getAttribute("course_number")[1:].strip()
    units = klass.getAttribute("units")
    section = klass.getAttribute("section")
    (section, section_type) = section.strip().split(" ")
    instructors = [klass.getAttribute("instructor").strip()]

    if len(klass.childNodes) > 0:
        section_note = klass.getElementsByTagName("note")[0].firstChild.data
    else:
        section_note = ""

    match = also_pattern.search(section_note)
    if match:
        instructors += filter(lambda x: x is not None, match.groups())

    try:
        semester = Semester("%s%s" % (season[:2], str(year)))

        if semester.season_name == "Summer" and number[0] == "N":
            number = number[1:]
            try:
                course = get_course(dpt, number)
            except Course.DoesNotExist:
                course = get_course(dpt, number, endswith = True)
        else:
            course = get_course(dpt, number)
    except Course.DoesNotExist, e:
        print "WARNING: creating course %s %s" % (dpt.abbr, number)
        course = Course(department=dpt, coursenumber=number, name=name, description="")
        course.save()
    except Exception, e:
        #tpls = "%s-%s-%s-%s-%s" % (dpt.abbr, number, instructor, season, year)
        #print "Couldn't match: " + tpls
        #if tpls not in bad_klasses:
        raise e
        #else:
        return


    try:
        kls = Klass.objects.get(course = course, semester=semester, section = section)
    except Klass.DoesNotExist:
        kls = Klass(course = course, semester=semester, section = section, section_type = section_type)
    kls.section_note = section_note
    kls.save()
    
    instrs = []
    for instructor in instructors:
        instructor = instructor.strip()
        if len(instructor) == 0 or instructor == "THE STAFF":
            continue
        try:
            inst = get_instructor(dpt, instructor)
        except Instructor.DoesNotExist:
            print "Could not find instructor: %s [%s]" % (instructor, dpt)
            inst = create_instructor(dpt, instructor)
        instrs.append(inst)
        

    for inst in instrs:
        if inst not in kls.instructors.all():
            kls.instructors.add(inst)


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
#    klassFiles = glob.glob(os.path.join(cd, "data/klass/xml/*2007*.xml"))
#    klassFiles += glob.glob(os.path.join(cd, "data/klass/xml/*2008*.xml"))
    klassFiles = glob.glob(os.path.join(cd, "data/klass/xml/*.xml"))
    for klassFile in klassFiles:
        print "Importing klasses from " + klassFile
        importFromXmlFile(klassFile)

if __name__ == "__main__":
    main()

