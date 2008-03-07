from django import newforms as forms
from string import atoi
import datetime
from django.core import urlresolvers
from hkn.main.widgets import JQueryAutoComplete, ModelAutocomplete
from hkn.exam.constants import EXAM_TYPE, VALID_EXTENSIONS
from hkn.course.constants import SEMESTER
from hkn.course.models import *
import os

class ExamForm(forms.Form):
    course = forms.CharField(widget = ModelAutocomplete("/course/course_autocomplete"))
    season = forms.ChoiceField(choices = SEMESTER.choices())
    year = forms.IntegerField(min_value = 1990, max_value = 2100)
    
    exam_type = forms.ChoiceField(choices = EXAM_TYPE.choices())
    
    number = forms.IntegerField(required = False)
    version = forms.CharField(required = False)
    is_solutions = forms.BooleanField()
    
    exam_file = forms.FileField()
    
    def clean_course(self):
        course_name = self.cleaned_data["course"]
        split = course_name.split(" ")
        if len(split) != 2:
            raise forms.ValidationError("Please format as \"DEPT NUM\" e.g. \"CS 61A\"")
        (dept_abbr, course_number) = split
        c = Course.objects.query_exact(dept_abbr, course_number)
        if len(c) == 0:
            raise forms.ValidationError("Course is not valid!")
        elif len(c) >= 2:
            raise forms.ValidationError("Matched more than one course!")
        self.cleaned_data["course_object"] = c[0]
        return c 
    
    def clean_exam_file(self):
        uf = self.cleaned_data["exam_file"]
        ext = os.path.splitext(uf.filename)[1]
        if ext not in VALID_EXTENSIONS:
            raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
        self.cleaned_data["exam_file_extension"] = ext
        return uf
        
    
    def clean_season(self):
        season_name = self.cleaned_data["season"]
        try:
            s = Season.objects.get(name = season_name)
        except Season.DoesNotExist:
            raise forms.ValidationError("Season is not valid!")
        self.cleaned_data["season_object"] = s
        return s
        
    def clean_year(self):
        yr = self.cleaned_data["year"]
        self.cleaned_data["year_object"] = datetime.datetime(yr, 1, 1)
        return yr
                                    
    def clean(self):
        d = self.cleaned_data
        if d.has_key("course_object") and d.has_key("season_object") and d.has_key("year_object"):
            klasses = Klass.objects.filter(course = d["course_object"], season = d["season_object"], year = d["year_object"])
            if len(klasses) == 0:
                raise forms.ValidationError("No klasses for that course and semester")
            elif len(klasses) >= 2:
                raise forms.ValidationError("More than 1 klass for that course and semester")
            self.cleaned_data["klass"] = klasses[0]
        return self.cleaned_data
            
            
            
            
        

