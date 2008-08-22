#!/usr/bin/env python

from course.models import *
from exam.models import *
from exam.constants import *

from find_klass import get_klass

import random, datetime

from django.core import serializers
from os import listdir
from os.path import isdir, join
import re

VALID_EXTENSIONS = ["html", "pdf", "ps", "txt"]

EE_DIR = "/home/gilbertchou/Projects/trunk/hkn/old_exams/ee"
CS_DIR = "/home/gilbertchou/Projects/trunk/hkn/old_exams/cs"
course_pattern = re.compile('^\d+[A-Z]*$')
course_map = {
	"COMPSCI" : CS_DIR,
	"EL ENG" : EE_DIR,
}

season_map = {
	"sp" : "Spring",
	"fa" : "Fall",
	"su" : "Summer",
}

def parse_filename(filename):
	info = filename.split('.')[0].split('-')
	try:
		num = int(info[1])
		type = EXAM_TYPE_MIDTERM
	except:
		num = 1
		type = EXAM_TYPE_FINAL
	
	return (season_map[info[0]], num, type, len(info) > 2)

def list_folders(path):
	return filter(lambda x: isdir(join(path, x)), listdir(path))

def is_valid_file(filename):
	try:
		parse_filename(filename)
		return filename.split(".")[1] in VALID_EXTENSIONS
	except:
		return False

def is_instructor_file(filename):
	try:
		return filename.split(".")[1] == "txt"
	except:
		return False

def list_files(path):
	return filter(lambda x: not isdir(join(path, x)), listdir(path))

def parse_instructor_file(path):
	f = open(path, "r")
	d = {}
	for line in f:
		try:
			line = re.split("[\t\n\r ]+", line)
			d[" ".join(  [line[0], line[1]] ) ] = line[2]
		except:
			print "Bad line in instructor file: %s" % line
	
	f.close()
	return d

def load_exams():
	"""   
	from exam.scripts.import_exams import load_exams
	load_exams()
	"""
	for dept, root in course_map.items():
		classes = filter(lambda x: course_pattern.match(x), list_folders(root))
		for c in classes:
			try:
				instructor_filename = join(root, c, filter(is_instructor_file, list_files(join(root, c)))[0])
			except:
				print "NO INSTRUCTOR FILE FOUND"
				continue
				
			instructor_map = parse_instructor_file(instructor_filename)
			for year in list_folders(join(root, c)):
				for filename in filter(is_valid_file, list_files(join(root, c, year))):
					season, number, type, solution = parse_filename(filename)
					try:
						instructor = instructor_map[season + " " + year]
						klass = get_klass(dept, c, instructor, season.lower(), year)
						f = open(join(root, c, year, filename) , "r")
						e = Exam()
						e.klass = klass
						e.file = f
						e.number = number
						e.is_solution = solution
						e.version = 0
						e.paper_only = False
						e.publishable = True
						e.exam_type = type
						e.topics = ""
						e.submitter = None
						e.save()
						f.close()
					except:
						print "Failed on %s %s %s" % (season, year, instructor )
	
def main():
	load_exams()
