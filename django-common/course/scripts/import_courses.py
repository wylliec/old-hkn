#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, os
from xml.dom import minidom

import setup_settings; setup_settings.setup(); os.chdir(setup_settings.get_cd())

from course.models import *

def importCourse(dpt, course):
    name = course.getAttribute("name")
    number = course.getAttribute("number")
    units = course.getAttribute("units")
    if len(course.childNodes) > 0:
        description = course.firstChild.data
    else:
        description = ""

    try:
        c = Course.objects.get(department = dpt, coursenumber = number)
    except Course.DoesNotExist:
        c = Course(department = dpt, coursenumber = number)
    c.department_abbr = dpt.abbr
    c.name = name
    c.description = description
    c.save()

def importDepartment(department):
    name = department.getAttribute('name').strip()
    abbr = department.getAttribute('abbr').strip()
    try:
        dpt = Department.objects.get(abbr__iexact = abbr)
    except Department.DoesNotExist:
        raise Exception, "department for abbr %s doesn't exist! " % (abbr, )

    for course in department.getElementsByTagName("course"):
        importCourse(dpt, course)

def importFromXmlFile(courseFile):
    dom = minidom.parse(file(courseFile, "r"))
    for department in dom.getElementsByTagName("department"):
        importDepartment(department)

def main():
    courseFiles = glob.glob("data/courses_xml/*.xml")

    for courseFile in courseFiles:
        print "Importing courses from " + courseFile
        importFromXmlFile(courseFile)

if __name__ == "__main__":
    main()

