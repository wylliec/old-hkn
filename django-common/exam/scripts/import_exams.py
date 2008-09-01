#!/usr/bin/env python

import setup_settings

from course.models import *
from exam.models import *
from exam.constants import *

from find_klass import *

from django.core.files.base import File
from os import listdir
from os.path import isdir, join, split
import re
import shutil
import sys
from settings import MEDIA_ROOT, SERVER_ROOT

VALID_EXTENSIONS = ["html", "pdf", "ps", "txt"]

#EE_DIR = join(SERVER_ROOT, "old_exams/ee")
#CS_DIR = join(SERVER_ROOT, "old_exams/cs")
EE_DIR = "/web/student/online/exams_import/ee"
CS_DIR = "/web/student/online/exams_import/cs"

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
	if info[1] == "f":
		num = "1"
		type = EXAM_TYPE_FINAL
	else:
		num = info[1]
		type = EXAM_TYPE_MIDTERM
	
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
	try:
		f = open(path, "r")
	except:
		return {}
		
	d = {}
	for line in f:
		try:
			line = re.split("[\t\n\r ]+", line)
			d[" ".join(  [line[0], line[1]] ) ] = line[2]
		except:
			print "Bad line in instructor file: %s" % line
	
	f.close()
	return d

def make_filename(klass, type, number, solution, extension):
	if type != EXAM_TYPE_FINAL:
		type_string = type + str(number)
	else:
		type_string = type
	
	if solution:
		sol_string = "_sol"
	else:
		sol_string = ""
		
	return "%s_%s_%s%s.%s" % (klass.course.short_name(), klass.semester.abbr(), type_string, sol_string, extension)

def load_exams():
	"""   
	import exam.scripts.import_exams as exam_loader
	exam_loader.load_exams()
	"""
	missing_instructor_file = []
	missing_instructors = set()
	missing_courses = set()
	missing_semesters = set()
	missing_klasses = set()
	instructor_mismatches = set()
	failed_imports = []
	
	for dept, root in course_map.items():
		try:
			os.mkdir(join(root, "completed"))
		except:
			pass
			
		classes = filter(lambda x: course_pattern.match(x), list_folders(root))
		for c in classes:
			try:
				instructor_filename = join(root, c, filter(is_instructor_file, list_files(join(root, c)))[0])
				instructor_map = parse_instructor_file(instructor_filename)
			except:
				print "NO INSTRUCTOR FILE FOUND"
				missing_instructor_file.append(dept + " " + c)
				instructor_map = {}
		
			for year in list_folders(join(root, c)):
				for filename in filter(is_valid_file, list_files(join(root, c, year))):
					season, number, type, solution = parse_filename(filename)
					try:
						instructor = instructor_map[season + " " + year]
						instructors = instructor.replace("_", " ").split("/")
					except:
						print "semester not found in instructor file or instructor file doesn't exist"
						instructors = []
					
					try:
						klass = get_klass(dept, c, instructors, season=season.lower(), year=year)
						klass = klass[0]
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
						new_filename = make_filename(klass, type, number, solution, filename.split('.')[-1])
						e.file.save(new_filename, File(f))
						e.save()
						f.close()
						shutil.move(join(root, c, year, filename), join(root, "completed", new_filename))
					except MissingInstructorException, e:
						print e[0]
						missing_instructors.add(e[1])
					except MissingCourseException:
						print "Course not found: %s %s:" % (dept, c)
						missing_courses.add("%s %s" % (dept, c))
					except InstructorMismatch, e:
						print e
						instructor_mismatches.add("%s" % (e))
					except NoKlasses, e:
						print "No Klasses found for %s %s - %s %s" % (dept, c, season, year)
						missing_klasses.add("%s %s - %s %s" % (dept, c, season, year))
					except Exception, e:
						print "Failed on %s %s %s" % (season, year, instructor )
						failed_imports.append("%s: %s %s %s %s" % (e, c, season, year, instructor) )
						
	
	print "Import completed!"
	print "Unexpected errors (%d): " % len(failed_imports)
	for msg in failed_imports:
		print msg
	print ""
	
	print "No Klass for the following: "
	print "\n".join(sorted(missing_klasses))
	print ""
	
	print "Semester not in instructor file: "
	print "\n".join(sorted(missing_semesters))
	print ""

	print "Courses with missing instructor files: " 
	print "\n".join(sorted(missing_instructor_file))
	print  ""
	
	print "Instructors that are missing: " 
	print "\n".join(sorted(missing_instructors))
	print ""
	
	print "Instructor mismatch: "
	print "\n".join(sorted(instructor_mismatches))
	print ""
	
	print "Courses that are missing: " + ", ".join(sorted(missing_courses))
	
	#return (missing_instructors, missing_courses, instructor_mismatches)

def main():
	load_exams()

if __name__ == "__main__":
	main()
