#!/usr/bin/env python

from course.models import *
from exam.models import *
from exam.constants import *

from find_klass import get_klass

from django.core.files.base import File
import sys
from os import listdir
from os.path import isdir, join, split
import re
import shutil
from settings import MEDIA_ROOT

VALID_EXTENSIONS = ["html", "pdf", "ps", "txt"]
filepattern = re.compile("^[a-zA-Z]+\d+[a-zA-Z]*_(sp|fa|su)\d\d_(mt\d+|f|q\d+)(_sol)?$")

def list_folders(path):
	return filter(lambda x: isdir(join(path, x)), listdir(path))

def is_valid_file(filename):
	try:
		base, ext = filename.split(".")
		return filepattern.match(base) and ext in VALID_EXTENSIONS
	except:
		return False

def list_files(path):
	return filter(lambda x: not isdir(join(path, x)), listdir(path))

def parse_filename(filename):
	bits = filename.split("_")
	return (bits[0], bits[1], bits[2], len(bits) > 3)

def parse_instructor_file(path):
	"""
	Instructor lines formatted like so:
		ee20 sp08 ayazifar
	"""
	try:
		f = open(path, "r")
	except:
		print "Instructor file not found."
		return {}
	
	d = {}
	for line in f:
		try:
			line = re.split("[\t\n\r ]+", line)
			d[" ".join(  [line[0], line[1]] ) ] = line[1]
		except:
			print "Bad line in instructor file: %s" % line
	
	f.close()
	return d
	
def add_exams(path):
	"""   
	from exam.scripts.add_exams import add_exams
	load_exams()
	"""
	d = parse_instructor_file(join(path, "instructor_file.txt"))
	
	for filename in list_files(path):
		if not is_valid_file(filename):
			print "Invalid file name: %s" % filename
			continue
		
		course, season, type, sol = parse_filename(filename)
		dept, coursenum = Course.parse_query(course)
		#course = Course.parse_query(dept, coursenum)
		#if course.count() != 1:
		#	print "Course name is ambiguous. -- %s" % course
		#	continue
		#course = course[0]
		
		try:	
			klass = get_klass(dept, course, instructor, season.lower(), year)
			e = Exam()
			e.klass = klass
			e.number = number
			e.is_solution = solution
			e.version = 0
			e.paper_only = False
			e.publishable = True
			e.exam_type = type
			e.topics = ""
			e.submitter = None
			f = open(join(root, c, year, filename) , "r")
			e.file.save(make_filename(klass, type, number, solution, filename.split('.')[-1]), File(f))
			e.save()
			f.close()
		except:
			print "Failed on %s %s %s" % (season, year, instructor )

def main():
	try:
		add_exams(sys.argv[1])
	except:
		"add_exams: Missing first argument (path to the folder of exams you want to add)" 
