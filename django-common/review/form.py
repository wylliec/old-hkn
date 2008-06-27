from django.newforms.models import ModelForm
from django import newforms as forms
from models import Problem
import os

VALID_EXTENSIONS = [".pdf"]

class ProblemForm(ModelForm):
	difficulty = forms.IntegerField(min_value=0, max_value=10)
	
	def clean_tags(self):
		uf = self.cleaned_data["tags"]
		
		if uf.find(',') == -1:
			uf = r'"' + uf + r'"'
		
		return uf
	
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
		exclude = ('num_ratings',)