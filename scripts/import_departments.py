#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob
from xml.dom import minidom

import hkn_settings

from course.models import *

def importDepartment(department):
	name = department.getAttribute('name').strip()
	abbr = department.getAttribute('abbr').strip()
	try:
		dpt = Department.objects.get(name__iexact = name, abbr__iexact = abbr)
	except Department.DoesNotExist:
		dpt = Department(name = name, abbr = abbr)
		dpt.save()

def importFromXmlFile(departmentFile):
	dom = minidom.parse(file(departmentFile, "r"))
	for department in dom.getElementsByTagName("department"):
		importDepartment(department)

def main():
    departmentFile = "klass/departments-sanitized.xml"
    print "Importing departments from " + departmentFile
    importFromXmlFile(departmentFile)

if __name__ == "__main__":
	main()

