from django import forms
from hkn.indrel.models import InfosessionRegistration
import os.path

class InfosessionRegistrationForm(forms.ModelForm):
    class Meta:
        model = InfosessionRegistration
