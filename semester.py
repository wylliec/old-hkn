#!/usr/bin/env python
import datetime
from string import atoi
from hkn.constants import HKN

"""The semester module handles semester related stuff.

In the database, semesters are stored as strings of the form:
    {ss}{yy}
    

Where ss is either sp or fa (for spring and fall, respectively) 
and yy is the last two digits of the year

e.g., fa07, sp08, etc.

This module provides some helper functions to get the current semester,
next semester, and semester start/end times.
"""


CURRENT_SEMESTER = HKN.SEMESTER
#CURRENT_SEMESTER = "fa07"

def getCurrentSemester():
    """Gets the current semester, in ssyy format, such as fa07, sp08"""
    return CURRENT_SEMESTER

def getSemesterStart(sem = getCurrentSemester()):
    """
    Gets the start time of the semester, assumed to be in ssyy format.
    Defaults to current semester.
    

    @type sem:	string
    @param sem: the semester, or current semester if not specified
    @rtype:	datetime
    @return: a datetime representing the beginning of the semester
    """
    s = sem[0:2]
    y = "20" + sem[2:4]
    if s == "fa":
        return datetime.datetime(atoi(y), 6, 1)
    else:
        return datetime.datetime(atoi(y), 1, 1)

def getSemesterEnd(sem = getCurrentSemester()):
    """
    Gets the end time of the semester, assumed to be in ssyy format.
    Defaults to current semester.
    

    @type sem:	string
    @param sem: the semester, or current semester if not specified
    @rtype:	datetime
    @return: a datetime representing the end of the semester
    """	
    s = sem[0:2]
    y = "20" + sem[2:4]
    if s == "fa":
        return datetime.datetime(atoi(y), 12, 31)
    else:
        return datetime.datetime(atoi(y), 5, 31)

def getNextSemester(sem = getCurrentSemester()):
    """
    For a given semester, returns the next semester.

    @type sem:	string
    @param sem: the semester, or current semester if not specified
    @rtype:	string
    @return: a semester string representing the next semester
    """
    

    s = sem[0:2]
    if s == "fa":
        y = atoi(sem[2:4]) + 1
        return "sp" + str(y).rjust(2, '0')
    else:
        return "fa" + sem[2:4]
