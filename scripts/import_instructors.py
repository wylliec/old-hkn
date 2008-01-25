#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, pdb
from xml.dom import minidom

import hkn_settings

from hkn.course.models import *
from hkn.course.constants import EXAMS_PREFERENCE

def importInstructor(dpt, instructor):
	first = instructor.getAttribute("first")
	middle = instructor.getAttribute("middle")
	last = instructor.getAttribute("last")

	try:
		c = Instructor.objects.get(department = dpt, first__iexact = first, last__iexact = last)
	except Instructor.DoesNotExist:
		c = Instructor(first=first, middle=middle, last=last, department = dpt)
		c.email = ""
		c.exams_preference = EXAMS_PREFERENCE.UNKNOWN
		c.distinguished_teacher = False

	c.distinguished_teacher = instructor.hasAttribute("distinguished") and instructor.getAttribute("distinguished").lower() == "true"
	c.save()
	

def importDepartment(department):
	abbr = department.getAttribute('abbr').strip()
	try:
		dpt = Department.objects.get(abbr__iexact = abbr)
	except Department.DoesNotExist:
		raise Exception, "department for abbr %s doesn't exist! " % (abbr, )

	for instructor in department.getElementsByTagName("instructor"):
		importInstructor(dpt, instructor)

def importFromXmlFile(instructorFile):
	dom = minidom.parse(file(instructorFile, "r"))
	for department in dom.getElementsByTagName("department"):
		importDepartment(department)

def main():
	instructorFiles = glob.glob("course/instructors_xml/*.xml")

	for instructorFile in instructorFiles:
		print "Importing instructors from " + instructorFile
		importFromXmlFile(instructorFile)

if __name__ == "__main__":
	main()

