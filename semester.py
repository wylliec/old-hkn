#!/usr/bin/env python2.4
import datetime
from string import atoi

CURRENT_SEMESTER = "sp08"
#CURRENT_SEMESTER = "fa07"

def getCurrentSemester():
	return CURRENT_SEMESTER

def getSemesterStart(sem = getCurrentSemester()):
	s = sem[0:2]
	y = "20" + sem[2:4]
	if s == "fa":
		return datetime.datetime(atoi(y), 6, 1)
	else:
		return datetime.datetime(atoi(y), 1, 1)

def getSemesterEnd(sem = getCurrentSemester()):
	s = sem[0:2]
	y = "20" + sem[2:4]
	if s == "fa":
		return datetime.datetime(atoi(y), 12, 31)
	else:
		return datetime.datetime(atoi(y), 5, 31)

def getNextSemester(sem = getCurrentSemester()):
	s = sem[0:2]
	if s == "fa":
		y = atoi(sem[2:4]) + 1
		return "sp" + str(y).rjust(2, '0')
	else:
		return "fa" + sem[2:4]
