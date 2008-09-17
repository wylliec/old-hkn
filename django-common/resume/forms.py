from django import forms
from string import atoi
import datetime
import decimal
from django.core import urlresolvers
from django.core.files.base import ContentFile
from nice_types import semester
import os

from resume.models import Resume

VALID_EXTENSIONS = (".doc", ".pdf")
class ResumeForm(forms.Form):
    overall_gpa = forms.DecimalField(label="Overall GPA", min_value=1, max_value=4)
    major_gpa = forms.DecimalField(label="Major GPA (optional)", min_value=1, max_value=4, required=False)
    text = forms.CharField(help_text="Paste the contents of your resume (used for searching)", label="Resume Text", widget=forms.Textarea())
    grad_semester = semester.SemesterSplitFormField(help_text="your intended graduation semester e.g. fa05 sp08", initial=semester.Semester(season_name="Spring", year=datetime.date.today().year + 2))

    resume = forms.FileField(help_text="please provide a doc or pdf", label="Resume")

    def clean_resume(self):
        uf = self.cleaned_data["resume"]
        ext = os.path.splitext(uf.name)[1]
        if ext not in VALID_EXTENSIONS:
            raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
        self.cleaned_data["resume_extension"] = ext
        return uf

    def bind_person(self, person):
        if  person.extendedinfo.grad_semester:
            self.fields['grad_semester'].initial = person.extendedinfo.grad_semester

    def save(self, person):
        d = self.cleaned_data
        try:
            r = person.resume
        except Resume.DoesNotExist:
            r = Resume(person=person)
        if d['major_gpa'] == None:
            r.major_gpa = decimal.Decimal("0.00")
        else:
            r.major_gpa=d['major_gpa']
        r.overall_gpa=d['overall_gpa']
        r.text=d['text']
        r.save_resume_file(d['resume'].read(), d['resume_extension'])
        person.extendedinfo.grad_semester = d['grad_semester']
        person.extendedinfo.save()
        r.save()
        return r
