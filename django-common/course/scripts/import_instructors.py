#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, pdb, os, os.path
from xml.dom import minidom

import setup_settings
cd = setup_settings.get_scripts_directory()

from course.models import *
from course.constants import EXAMS_PREFERENCE

merged = []
def import_instructor(dpt, instructor):
    first = instructor.getAttribute("first")
    middle = instructor.getAttribute("middle")
    last = instructor.getAttribute("last")
    
    instructors = Instructor.objects.hinted_query(last_name=last, first_name=first, force_first=True, department_abbrs = (dpt.abbr,))
    if len(instructors) == 0:
        c = Instructor(first=first, middle=middle, last=last, home_department = dpt)
        c.email = ""
        c.exams_preference = EXAMS_PREFERENCE.UNKNOWN
        c.distinguished_teacher = instructor.hasAttribute("distinguished") and instructor.getAttribute("distinguished").lower() == "true"    
        c.save()
        return
    elif len(instructors) == 1:
        c = instructors[0]
    else:
        print "UH-OH Many instructors match! We should look into this"
        # probably not a good idea, but we never hit this code....
        c = instructors[0]
        
    c.distinguished_teacher = instructor.hasAttribute("distinguished") and instructor.getAttribute("distinguished").lower() == "true"    
    
    if c.departments.filter(pk = dpt.id).count() == 0:
        if first == c.first or \
            ((first, last), (c.first, c.last)) in ((("Karl", "Pister"), ("Kristofer", "Pister")),):
            print "Merging %s: %s -> %s" % (last, str((first, dpt)), str((c.first, c.departments.all())))
            c.departments.add(dpt)
            merged.append(c)
        elif ((first, last), (c.first, c.last)) in ((("Peter", "Bartlett"), ("Paul", "Bartlett")),):
            print "Mismatched first name and department for %s: %s -> %s" % (last, str((first, dpt)), str((c.first, c.departments.all())))
            c = Instructor(first=first, middle=middle, last=last, home_department = dpt)
            c.email = ""
            c.exams_preference = EXAMS_PREFERENCE.UNKNOWN
            c.distinguished_teacher = instructor.hasAttribute("distinguished") and instructor.getAttribute("distinguished").lower() == "true"    

    c.save()
    return

def import_department(department):
    abbr = department.getAttribute('abbr').strip()
    try:
        dpt = Department.objects.get(abbr__iexact = abbr)
    except Department.DoesNotExist:
        raise Exception, "department for abbr %s doesn't exist! " % (abbr, )

    for instructor in department.getElementsByTagName("instructor"):
        import_instructor(dpt, instructor)

def importFromXmlFile(instructorFile):
    dom = minidom.parse(file(instructorFile, "r"))
    for department in dom.getElementsByTagName("department"):
        import_department(department)

def main():
    instructorFiles = glob.glob(os.path.join(cd, "data/instructors_xml/*.xml"))

    for instructorFile in instructorFiles:
        print "Importing instructors from " + instructorFile
        importFromXmlFile(instructorFile)

if __name__ == "__main__":
    main()

