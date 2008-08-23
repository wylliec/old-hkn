#!/usr/bin/env python
import sys, os

import hkn_settings
from photologue.models import GalleryUpload
from nice_types.semester import Semester
from django.core.files.base import ContentFile

remoteaddr = "hkn.eecs.berkeley.edu"

def import_gallery(semester, zipfilename, title, desc):
	galleryupload = GalleryUpload()

	galleryupload.semester = Semester(semester)
	galleryupload.title = title
	galleryupload.description = desc

	zipfile = ContentFile(file(zipfilename).read())
	galleryupload.zip_file.save("galleryupload.zip", zipfile)

def import_semester(semester, workdir):
	remoteSemester = semester
	if semester[0:2] == "fa":
		remoteSemester = "fl" + semester[2:]

	semesterdir = "%s/%s" % (workdir, semester)
	try:
		os.mkdir(semesterdir)
	except:
		pass

	os.system("scp %s:/web/yearbook/%s/event_list.txt %s" % (remoteaddr, remoteSemester, semesterdir))
	f = open("%s/event_list.txt" % (semesterdir), "r")

	for line in f:
		if line.find(";") < 0:
			continue
		temp = [x.strip() for x in line.split(";", 2)]
		if len(temp) == 3:
			dir, date, title = temp
		else:
			dir = temp[0]
			temp2 = temp[1].split(":", 1)
			if len(temp2) == 2:
				date, title = temp2
			else:
				date = ""
				title = ""
				print "Parsing problem for %s", line

		print "Importing %s for %s" % (title, semester)

		status = os.system("rsync -a --no-perms --chmod=Fa-x -e ssh %s:/web/yearbook/%s/%s/originals/ %s/%s" % (remoteaddr, remoteSemester, dir, semesterdir, dir))
		if status != 0:
			continue
		zipfilename = "%s/%s.zip" % (semesterdir, dir)
		status = os.system("zip -q -0 %s %s/%s/*" % (zipfilename, semesterdir, dir))
		if status != 0:
			continue

		os.system("scp %s:/web/yearbook/%s/%s/title.txt %s/%s/" % (remoteaddr, remoteSemester, dir, semesterdir, dir))
		titleFile = open("%s/%s/title.txt" % (semesterdir, dir))
		desc = titleFile.read()
		titleFile.close()

		import_gallery(semester, zipfilename, title, desc)

		os.remove(zipfilename)
		rmrf("%s/%s" % (semesterdir, dir))
	f.close()
	rmrf(semesterdir)

def rmrf(dir):
	for root, dirs, files in os.walk(dir, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
	os.rmdir(dir)

def main(semesters):
	if len(semesters) == 0:
		print "Usage: ./import_yearbook_semesters sp08 fa07"
		print "Error: specify semesters to import as arguments"

	workdir = "galleryUpload"
	try:
		os.mkdir(workdir)
	except:
		pass

	for semester in semesters:
		import_semester(semester, workdir)

	rmrf(workdir)

if __name__ == '__main__':
	main(sys.argv[1:])
