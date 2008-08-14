#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle, glob, pdb
from xml.dom import minidom

import hkn_settings

from course.models import *
from course.constants import EXAMS_PREFERENCE, SEMESTER

def main():
	try:
		s = Season.objects.get(name=SEMESTER.SPRING)
		print "Spring exists"
	except:
		s = Season(name = SEMESTER.SPRING, order = 1)
	s.save()
	try:
		s = Season.objects.get(name=SEMESTER.SUMMER)
		print "Summer exists"
	except:
		s = Season(name = SEMESTER.SUMMER, order = 2)
	s.save()
	try:
		s = Season.objects.get(name=SEMESTER.FALL)
		print "Fall exists"
	except:
		s = Season(name = SEMESTER.FALL, order = 3)
	s.save()


if __name__ == "__main__":
	main()
