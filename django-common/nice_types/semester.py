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
    @staticmethod
    def for_semester(semester):
        season = semester.lower()[:2]
        year = int(semester[2:])
        return Semester(season_name=season, year=year)

    @staticmethod
    def for_date(date):
        def get_season():
            months = _SEASON_END_MONTHS.items()
            months.sort(key=lambda x: x[1])
            for month in months:
                if date.month <= month[1]:
                    return _SEASON_NAMES[month[0]]
            return None
        return Semester(season_name=get_season(), year=date.year)

    def __init__(self, semester=None, season_name=None, year=None):
        try:
            if semester is not None:
                self.season = semester.lower()[:2]
                self.year = int(semester[2:])
            elif season_name is not None and year is not None:
                self.season = season_name.lower()[:2]
                self.year = int(year)
            else:
                raise InvalidSemester("Need to specify either semester or season_name and year")
        except (IndexError, ValueError), e:
                raise InvalidSemester("Semester value provided is invalid")

        self.semester = "%s%s" % (self.season, str(self.year%100).rjust(2, "0"))
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
        return "%s %d" % (self.season_name.capitalize(), self.year)

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
            y = self.year+1
            return Semester("%s%s" % ("sp", y))
        else:
            y = self.year
            return Semester("%s%s" % ("fa", y))
        
    @property
    def previous_semester(self):
        s = self.semester[:2]
        if s == "sp":
            y = self.year-1
            return Semester("%s%s" % ("fa", y))
        else:
            y = self.year%100            
            return Semester("%s%s" % ("sp", y))

        
def current_semester():
    """Gets the current semester, in ssyy format, such as fa07, sp08"""
    from hkn.main.property import PROPERTIES
    return Semester(PROPERTIES.semester)

def current_year():
    return current_semester().year

from django.db import models
import types

class SemesterField(models.CharField):
    """ 
    handles serializing a semester to the database in the following format:
    <sort_prefix><separator><semester> e.g.
    
    sort_prefix will be a date, separator is unique, semester is e.g. fa2007
    """
    __metaclass__ = models.SubfieldBase
    SEPARATOR = "__SEMESTER__"
    PREFIX_DATE_FORMAT = "%Y%m%d"
    """ a format like 20080822 """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 30
        super(SemesterField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not type(value) in types.StringTypes:
            return value
        try:
            semester = value.split(SemesterField.SEPARATOR)
            assert len(semester) == 2
            return Semester(semester[1])
        except:
            return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if type(value) in types.StringTypes:
            if len(value.split(SemesterField.SEPARATOR)) == 2:
                return value
            else:
                value = Semester(value)
        if type(value) == Semester:
            return "%s%s%s" % (value.start_date.strftime(SemesterField.PREFIX_DATE_FORMAT),
                               SemesterField.SEPARATOR,
                               value.abbr())
        return value

from django import forms

_GRAD_SEASON_CHOICES = (("sp", "Spring"), ("fa", "Fall"))

class SplitSeasonYearWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Select(choices=_GRAD_SEASON_CHOICES, attrs=attrs),
            forms.Select(choices=[(str(x), str(x)) for x in range(2015, 2005, -1)], attrs=attrs),
        )
        super(SplitSeasonYearWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.season_name, value.year]
        return [None, None]

class SemesterSplitFormField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=_GRAD_SEASON_CHOICES),
            forms.ChoiceField(choices=[(str(x), str(x)) for x in range(2015, 2005, -1)]),
        )
        self.widget = SplitSeasonYearWidget
        super(SemesterSplitFormField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] in (None, ''):
            raise forms.ValidationError("Enter a valid season")
        if data_list[1] in (None, ''):
            raise forms.ValidationError("Enter a valid year")
        return Semester(season_name=data_list[0], year=data_list[1])

class SemesterFormField(forms.CharField):
    def clean(self, value):
        try:
            return Semester(value)
        except InvalidSemester, e:
            raise forms.ValidationError("Semester is invalid; ensure the format is similar to 'fa05' or 'sp08'")
