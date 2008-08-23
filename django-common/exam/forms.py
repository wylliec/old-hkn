from django import forms
from string import atoi
import datetime
from django.core import urlresolvers

from ajaxwidgets.widgets import JQueryAutoComplete, ModelAutocomplete
from course.constants import SEMESTER
from course.models import *
import os

from constants import EXAM_TYPE, VALID_EXTENSIONS

class ExamForm(forms.Form):
    course = forms.CharField(widget = ModelAutocomplete("/course/course_autocomplete"))
    instructor = forms.CharField(widget = ModelAutocomplete("/course/instructor_autocomplete"))
    semester = forms.CharField(help_text="The semester e.g. fa05, sp08", max_length=4)
    
    exam_type = forms.ChoiceField(choices = EXAM_TYPE.choices())
    
    number = forms.IntegerField(required = False)
    version = forms.CharField(required = False)
    is_solutions = forms.BooleanField()
    
    exam_file = forms.FileField()
    
    def clean_course(self):
        course_name, course_id = self.cleaned_data["course"].split("|")
        split = course_name.split(" ")
        if len(split) != 2:
            raise forms.ValidationError("Please format as \"DEPT NUM\" e.g. \"MATH 1B\"")
        (dept_abbr, course_number) = split

        try:
            c = Course.objects.get(pk=course_id)
            if not c.number == course_number:
                raise forms.ValidationError("Please re-enter course; received conflicting values")
        except Course.DoesNotExist, ValueError:
            c = Course.objects.query_exact(dept_abbr, course_number)
            if len(c) == 0:
                raise forms.ValidationError("Course is not valid!")
            elif len(c) >= 2:
                raise forms.ValidationError("Matched more than one course!")
            c = c[0]

        self.cleaned_data["course_object"] = c
        return c 

    def clean_semester(self):
        try:
            self.cleaned_data["semester_object"] = Semester(self.cleaned_data["semester"])
        except:
            raise forms.ValidationError("Semester is invalid; ensure the format is similar to 'fa05'")
        return self.cleaned_data["semester_object"]
    
    def clean_exam_file(self):
        uf = self.cleaned_data["exam_file"]
        ext = os.path.splitext(uf.name)[1]
        if ext not in VALID_EXTENSIONS:
            raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
        self.cleaned_data["exam_file_extension"] = ext
        return uf
        
    def filter_klasses_by_instructor(self, klasses):
        instructor_name, instructor_id = self.cleaned_data["instructor"].split("|")
        try: 
            instructor = Instructor.objects.get(pk=instructor_id)
            return klasses.filter(instructor = instructor)
        except Instructor.DoesNotExist:
            instructors = Instructor.objects.query(instructor_name)
            return klasses.filter(instructor__in = instructors)


    def clean(self):
        d = self.cleaned_data
        if d.has_key("course_object") and d.has_key("semester_object"):
            klasses = Klass.objects.filter(course = d["course_object"], semester=d["semester_object"])
            if len(klasses) == 0:
                raise forms.ValidationError("No klasses for that course and semester")
            elif len(klasses) >= 2:
                potential_instructors = ", ".join([k.instructor_names() for k in klasses])
                klasses = self.filter_klasses_by_instructor(klasses)
                if len(klasses) == 0:
                    raise forms.ValidationError("More than 1 klass for that course and semester, but the provided instructor didn't teach any sections; try specifying an instructor from: %s" % (potential_instructors,))
                elif len(klasses) >= 2:
                    raise forms.ValidationError("More than 1 klass for that course, semester, and instructor; try specifying an instructor from %s" % (potential_instructors,))
            self.cleaned_data["klass"] = klasses[0]
        return self.cleaned_data
            
