from django import forms
from string import atoi
import datetime
from django.core import urlresolvers
import os

class ResumeForm(forms.Form):
    major_gpa = forms.DecimalField(label="Major GPA", min_value=1.0, max_value=4.0)
    overall_gpa = forms.DecimalField(label="Overall GPA", min_value=1.0, max_value=4.0)
    text = forms.CharField(help_text="Paste the contents of your resume (used for searching)", label="Resume Text", widget=forms.Textarea())
#    comment = forms.CharField(label = "Anything We Should Know?", required = False, widget=forms.Textarea(attrs={'rows' : 2, 'wrap' : 'virtual'}))

    resume = forms.FileField(help_text="please provide a doc or pdf", label="Resume")

