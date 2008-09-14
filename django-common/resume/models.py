import datetime, re, os, string, os.path

from hkn.info.models import Person

import request.utils
from django.db.models.query import QuerySet
from nice_types.db import QuerySetManager
from nice_types.semester import Semester

from django.db import models

class Concentration(models.Model):
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=20)

class Resume(models.Model):
    person = models.OneToOneField(Person)
    resume = models.FileField(upload_to="resumes", max_length=200)
    submitted = models.DateTimeField(auto_now=True)
    major_gpa = models.DecimalField(decimal_places=2, max_digits=3)
    overall_gpa = models.DecimalField(decimal_places=2, max_digits=3)
    text = models.TextField()
    published = models.BooleanField()
    concentrations = models.ManyToManyField(Concentration, related_name="resumes")
    
    def describe_gpa(self):
        gpa = "GPA: %s"
        gpas = []
        if self.major_gpa and self.major_gpa > 0:
            gpas.append("%s (major)" % self.major_gpa)
        if self.overall_gpa and self.overall_gpa > 0:
            gpas.append("%s (overall)" % self.overall_gpa)
        return gpa % ", ".join(gpas)

from resume.admin import *
