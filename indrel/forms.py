from django import forms
from hkn.indrel.models import InfosessionRegistration, ResumeBookOrder
import os.path

class InfosessionRegistrationForm(forms.ModelForm):
    class Meta:
        model = InfosessionRegistration

class ResumeBookOrderForm(forms.ModelForm):
    class Meta:
        model = ResumeBookOrder
