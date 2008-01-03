from django.db import models
from hkn.info.models import *
from hkn.auth.models import *
from hkn.event.models import *

from django import newforms as forms
import os

class CandidateApplicationForm(forms.Form):
	first = forms.CharField()
	real_first = forms.CharField()
	last = forms.CharField()
	
	local_phone = forms.CharField()
	perm_phone = forms.CharField()
	local_addr = forms.CharField()
	perm_addr = forms.CharField()
	school_email = forms.CharField()
	preferred_email = forms.CharField()
	sid = forms.CharField()

	year = forms.ChoiceField(choices = APP_YEAR.choices())
	transfer = forms.BooleanField(required = True)
	transferred_from = forms.CharField(required = False)
	
	option = forms.ChoiceField(choices = EECS_OPTION.choices())
	grad_semester = forms.CharField()
	
	committee_prefs = forms.CharField()

	q1 = forms.CharField()
	q2 = forms.CharField()
	q3 = forms.CharField()
	q4 = forms.CharField()
	q5 = forms.CharField()

