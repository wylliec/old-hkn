#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob
from xml.dom import minidom

import hkn_settings

from hkn.course.models import *

def importKlass(dpt, klass, year, season):
	raise Exception, "Unimplemented because no instructor data yet exists!"
	name = klass.getAttribute("name")
	number = klass.getAttribute("number")
	units = klass.getAttribute("units")
	if len(klass.childNodes) > 0:
		description = klass.firstChild.data
	else:
		description = ""

	try:
		c = Course.objects.get(department = dpt, number = number)
	except:
		c = Course(department = dpt, number = number)
	c.department_abbr = dpt.abbr
	c.name = name
	c.description = description
	c.save()

def importDepartment(department, year, season):
	abbr = department.getAttribute('abbr')	
	try:
		dpt = Deparment.objects.get(abbr__iexact = abbr.upper())
	except Exception, e:
		raise Exception, "Couldn't find department with abbreviation %s and can't create (don't know full name)!" % (abbr, )
	
	for klass in department.getElementsByTagName("klass"):
		importKlass(dpt, klass, year, season)

def importSemester(semester):
	year = semester.getAttribute("year")
	season = semester.getAttribute("season")
	for department in semester.getElementsByTagName("department"):
		importDepartment(department, year, season)

def importFromXmlFile(klassFile):
	dom = minidom.parse(file(klassFile, "r"))
	for semester in dom.getElementsByTagName("semester"):
		importSemester(semester)

klassFiles = glob.glob("course/klasses_xml/*.xml")

for klassFile in klassFiles:
	print "Importing klasses from " + klassFile
	print "except that I won't because there's no instructor data!"
	import sys
	sys.exit()
	importFromXmlFile(klassFile)

