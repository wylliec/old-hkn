#!/usr/bin/env python
import setup_settings

from course.models import *
from exam.models import *
from exam.constants import *

from find_klass import *

from django.core.files.base import File
import sys
from os import listdir
from os.path import isdir, join, split
import re
import shutil
from settings import SERVER_ROOT, MEDIA_ROOT

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
			d[" ".join(  [line[0], line[1]] ) ] = line[2]
		except:
			print "Bad line in instructor file: %s" % line
	
	f.close()
	return d


def convert_file(path):
	path_without_extension = path.split('.')[0]
	extension = path.split('.')[1]
	
	if extension == 'html':
		if os.path.exists(path_without_extension + ".pdf"):
			os.system("rm " + path)
			print "PDF exists, deleting file: " + path
			return
			
		os.system("htmldoc -f " + path_without_extension + ".pdf --webpage " + path)
		os.system("rm " + path)
		print "Converting html to pdf: " + path
	elif extension == 'ps':
		if os.path.exists(path_without_extension + ".pdf"):
			os.system("rm " + path)
			print "PDF exists, deleting file: " + path
			return
			
		os.system("ps2pdf " + path + " " + path_without_extension + ".pdf")
		os.system("rm " + path)
		print "Converting ps to pdf: " + path

def convert_exams(path):
	for filename in filter(is_valid_file, list_files(path)):
		convert_file(join(path, filename))

	
def add_exams(path):
	d = parse_instructor_file(join(path, "instructor_file.txt"))
	try:
		os.mkdir(join(path, "completed"))
	except:
		pass
	
	for filename in list_files(path):
		if not is_valid_file(filename):
			print "Invalid file name: %s" % filename
			continue
		elif os.path.exists(join(SERVER_ROOT, MEDIA_ROOT, FILE_UPLOAD_DIR, filename)):
			print "File exists: %s" % filename
			continue
		elif filename == "instructor_file.txt":
			continue
			
		course, semester, type, sol = parse_filename(filename)
		dept, coursenum = re.match("(cs|ee)(\w+)", course).groups()
		type, number = re.match("(mt|f|q)(\d*)", type).groups()
		if number == '':
			number = '1'
		
		instructors = d.get(" ".join([course, semester]), None)
		if not instructors:
			instructors = []
		else:
			instructors = instructors.replace("_", " ").split("/")
			
		try:	
			klass_pair = get_klass(dept, coursenum, instructors, semester=semester)
			klass = klass_pair[0]
			e = Exam()
			e.klass = klass
			e.number = number
			e.is_solution = sol
			e.version = 0
			e.paper_only = False
			e.publishable = True
			e.exam_type = EXAM_REVERSE_MAP[type]
			e.topics = ""
			e.submitter = None
			f = open(join(path, filename) , "r")
			e.file.save(filename, File(f))
			e.save()
			f.close()
			shutil.move(join(path, filename), join(path, "completed", filename))
		except Exception, e:
			print "Failed on %s" % (filename)
			print e

def main():
	try:
		add_exams(sys.argv[1])
	except:
		print "add_exams: Missing first argument (path to the folder of exams you want to add)" 

if __name__ == "__main__":
	main()

"""
import exam.scripts.add_exams as adder
path = '/home/gilbertchou/Desktop/sp08/'
from course.models import *
from nice_types.semester import *
c = Course.objects.query_exact("cs", "188")
c = c[0]
k = Klass.objects.filter(course=c, semester=Semester.for_semester("fa07"))
k = k[0]
"""
