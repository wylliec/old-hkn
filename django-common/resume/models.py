import datetime, re, os, string, os.path

from hkn.info.models import Person

import request.utils
from django.db.models.query import QuerySet
from django.core.files.base import ContentFile
from nice_types.db import QuerySetManager
from nice_types.semester import Semester, current_semester

from django.db import models

import random

class Concentration(models.Model):
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=20)

class ResumeManager(QuerySetManager):
    def for_current_semester(self, *args, **kwargs):
        return self.get_query_set().for_current_semester(*args, **kwargs)

_NON_SAFE_CHARACTERS = re.compile("[^-\w ]")
_WHITESPACE = re.compile("\s+")
class Resume(models.Model):
    objects = ResumeManager()

    person = models.OneToOneField(Person)
    resume = models.FileField(upload_to="resumes", max_length=200)
    submitted = models.DateTimeField(auto_now=True)
    major_gpa = models.DecimalField(decimal_places=2, max_digits=3)
    overall_gpa = models.DecimalField(decimal_places=2, max_digits=3)
    text = models.TextField()
    published = models.BooleanField()
    concentrations = models.ManyToManyField(Concentration, related_name="resumes")

    class QuerySet(QuerySet):
        def for_current_semester(self):
            semester = current_semester()
            return self.filter(submitted__gt=semester.start_date, submitted__lt=semester.end_date)

    def generate_filename(self, extension):
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        new = "%s-%s%s" % (''.join([random.choice(digits) for i in xrange(15)]), self.person.username, extension)
        return new

    def is_word(self):
        return self.resume.name.endswith(".doc") or self.resume.name.endswith(".docx")

    def save_resume_file(self, content, extension):
        self.resume.save(self.generate_filename(extension), ContentFile(content))
    
    def describe_gpa(self):
        gpa = "GPA: %s"
        gpas = []
        if self.major_gpa and self.major_gpa > 0:
            gpas.append("%s (major)" % self.major_gpa)
        if self.overall_gpa and self.overall_gpa > 0:
            gpas.append("%s (overall)" % self.overall_gpa)
        return gpa % ", ".join(gpas)

    def save(self, *args, **kwargs):
        if isinstance(self.text, unicode):
            self.text = self.text.encode('utf-8', 'xmlcharrefreplace')
        self.text = _WHITESPACE.sub(" ", _NON_SAFE_CHARACTERS.sub(" ", self.text))
        super(Resume, self).save(*args, **kwargs)

from resume.admin import *
