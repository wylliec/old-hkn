from django.newforms.models import ModelForm
from django import newforms as forms
from models import Problem
import os

VALID_EXTENSIONS = [".pdf"]

class ProblemForm(ModelForm):
	
	def clean_question(self):
		uf = self.cleaned_data["question"]
		ext = os.path.splitext(uf.filename)[1]
		if ext not in VALID_EXTENSIONS:
			raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
		return uf
			
	def clean_answer(self):
		uf = self.cleaned_data["answer"]
		ext = os.path.splitext(uf.filename)[1]
		if ext not in VALID_EXTENSIONS:
			raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
		return uf
		
		
	class Meta:
		model = Problem