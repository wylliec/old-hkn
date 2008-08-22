#!/usr/bin/env python
import datetime
from string import atoi

"""The semester module handles semester related stuff.

In the database, semesters are stored as strings of the form:
    {ss}{yy}
    

Where ss is either sp or fa (for spring and fall, respectively) 
and yy is the last two digits of the year

e.g., fa07, sp08, etc.

This module provides some helper functions to get the current semester,
next semester, and semester start/end times.
"""

_SEASON_MONTHS = {"sp" : 1, "su" : 6, "fa" : 8}
_SEASON_END_MONTHS = {"sp" : 5, "su" : 7, "fa" : 12}
_SEASON_MONTHS_REVERSE = {1 : "sp", 6 : "su", 8 : "fa"}
_SEASON_NAMES = {"sp" : "spring", "fa" : "fall", "su" : "summer"}

class InvalidSemester(Exception):
    pass

class Semester(object):
    def __init__(self, semester=None, season_name=None, year=None):
        if semester is not None:
            self.season = semester.lower()[:2]
            self.year = int(semester[2:])
        elif season_name is not None and year is not None:
            self.season = season_name.lower()[:2]
            self.year = int(year)
        else:
            raise InvalidSemester("Need to specify either semester or season_name and year")

        self.semester = "%s%d" % (self.season, self.year%100)
        try:
            self.season_name = _SEASON_NAMES[self.season]
        except KeyError:
            raise InvalidSemester("%s is not a valid season" % self.season)
            

        if self.year < 100:
            self.year += 1900
            if self.year < 1960:
                self.year += 100

    def __str__(self):
        return self.abbr()
    
    def abbr(self):
        return self.semester
    
    def verbose_description(self):
        return "%s %d" % (self.season_name, self.year)

    @property
    def start_date(self):
        return datetime.date(self.year, _SEASON_MONTHS[self.season], 1)

    @property
    def end_date(self):
        return datetime.date(self.year, _SEASON_END_MONTHS[self.season], 30)

    @property
    def next_semester(self):
        s = self.semester[:2]
        if s == "fa":
            y = self.year_int+1
            return Semester("%s%s" % ("sp", y))
        else:
            y = self.year_int
            return Semester("%s%s" % ("fa", y))
        
    @property
    def previous_semester(self):
        s = self.semester[:2]
        if s == "sp":
            y = self.year_int-1
            return Semester("%s%s" % ("fa", y))
        else:
            y = (self.year_int)%100            
            return Semester("%s%s" % ("sp", y))

        
def current_semester():
    """Gets the current semester, in ssyy format, such as fa07, sp08"""
    from hkn.main.property import PROPERTIES
    return Semester(PROPERTIES.semester)

def current_year():
    return current_semester().year

from django.db import models

class SemesterField(models.DateField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        value = super(models.DateField, self).to_python(value)
        try:
            season = _SEASON_MONTHS_REVERSE[value.month]
            return Semester("%s%s" % (season, value.year))
        except:
            return value

    def get_db_prep_value(self, value):
        if type(value) == type(""):
            value = Semester(value)
        return super(models.DateField, self).get_db_prep_value(value.start_date)
        
