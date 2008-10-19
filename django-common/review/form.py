from django.forms.models import ModelForm
from django import forms
from review.models import Problem
import os

VALID_EXTENSIONS = [".pdf"]

class ProblemForm(ModelForm):
	difficulty = forms.ChoiceField(choices=[("1", 1), ("2", 2), ("3", 3) , ("4", 4), ("5", 5) , ("6", 6), ("7", 7), ("8", 8), ("9", 9), ("10", 10)])
	
	def clean_tags(self):
		uf = self.cleaned_data["tags"]
		if uf == '':
			raise forms.ValidationError("Must have at least one tag.")
		
		if uf.find(',') == -1:
			uf = r'"' + uf + r'"'
		
		return uf
		
	def clean_question(self):
		uf = self.cleaned_data["question"]
		print type(uf)
		ext = os.path.splitext(uf.name)[1]
		if ext not in VALID_EXTENSIONS:
			raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
		return uf
			
	def clean_answer(self):
		uf = self.cleaned_data["answer"]
		ext = os.path.splitext(uf.name)[1]
		if ext not in VALID_EXTENSIONS:
			raise forms.ValidationError("Filetype must be one of: " + ", ".join(VALID_EXTENSIONS))
		return uf
		
		
	class Meta:
		model = Problem
		exclude = ('num_ratings', 'submitter', 'submitted',)
