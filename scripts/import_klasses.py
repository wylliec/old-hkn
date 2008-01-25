#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, datetime, pdb
from string import atoi
from xml.dom import minidom

import hkn_settings

from hkn.course.models import *

def getInstructor(dpt, name):
	names = name.replace(",", "").split(" ")
	(first, middle, last) = (None, None, None)
	last = names[0]
	if len(names) == 2:
		first = names[1]
	if len(names) == 3:
		middle = names[2]

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

	objects = objects.filter(middle__istartswith = middle)
	if len(objects) == 1:
		return objects[0]
	elif len(objects) == 0:
		raise Instructor.DoesNotExist, "could not find instructor with lastname, firstname, department, and middlename!"

	raise Instructor.DoesNotExist, "too many after all filters! " + str(objects)
	
def getCourse(dpt, number):
	return Course.objects.get(department = dpt, number=number)

def getSeason(season):
	return Season.objects.get(name__iexact = season)
	

def importKlass(dpt, klass, year, season):
	name = klass.getAttribute("name")
	number = klass.getAttribute("number")
	units = klass.getAttribute("units")
	section = klass.getAttribute("section")
	instructor = klass.getAttribute("instructor")

	if len(klass.childNodes) > 0:
		section_note = klass.getElementsByTagName("note")[0].firstChild.data
	else:
		section_note = ""

	try:
		course = getCourse(dpt, number)
		ssn = getSeason(season)
		yr = datetime.date(month=1, day=1, year=atoi(year))
	except Exception, e:
		print "%s %s %s %s %s" % (dpt, number, instructor, season, year)
		raise e


	try:
		kls = Klass.objects.get(course = course, season = ssn, year = yr, section = section)
	except Klass.DoesNotExist:
		kls = Klass(course = course, season = ssn, year = yr, section = section)
	kls.section_note = section_note

	kls.save()

	try:
		if len(instructor.strip()) > 0:
			inst = getInstructor(dpt, instructor)
		else:
			inst = None
	except Instructor.DoesNotExist:
		print "Could not find instructor: " + instructor
		inst = None
		

	if inst:
		if inst not in kls.instructor_set.all():
			kls.instructor_set.add(inst)


def importDepartment(department, year, season):
	abbr = department.getAttribute('abbr')	
	try:
		dpt = Department.objects.get(abbr__iexact = abbr.upper())
	except Department.DoesNotExist:
		raise Exception, "Couldn't find department with abbreviation %s and can't create (don't know full name)!" % (abbr, )
	
	for klass in department.getElementsByTagName("klass"):
		if klass.hasAttribute("number_type") and klass.getAttribute("number_type") == "P":
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
def main():
	klassFiles = glob.glob("course/klasses_xml/*.xml")

	for klassFile in klassFiles:
		print "Importing klasses from " + klassFile
		importFromXmlFile(klassFile)

if __name__ == "__main__":
	main()

