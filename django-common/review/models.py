import datetime
from django.contrib.auth.models import User, Permission
from django.db import models
import tagging
from tagging import fields
from tagging.models import Tag

FILE_UPLOAD_DIR =  'review'

class Problem(models.Model):
	
	name = models.CharField(max_length = 150)
	description = models.TextField(blank = True)
	tags = fields.TagField()
	difficulty = models.FloatField(null = True, blank = True)
	question = models.FileField(null = True, upload_to = FILE_UPLOAD_DIR)
	answer = models.FileField(null = True, upload_to = FILE_UPLOAD_DIR)
	submitted = models.DateTimeField()
	submitter = models.ForeignKey(User, null = True)
	
	num_ratings = models.IntegerField(default = 1)
	
	
	def tag_list(self):
		return tagging.utils.parse_tag_input(self.tags)
	
	def tag_objects(self):
		return Tag.objects.usage_for_model(Problem, filters={'pk':self.id})
	
	def add_tag(self, tag):
		self.tags = " ".join(self.tag_list() + [tag])
	
	def edit_tag(self, old, new):
		try:
			temp_tags = self.tag_list()
			temp_tags.remove(old)
			temp_tags.append(new)
			self.tags = " ".join(temp_tags)
		except ValueError:
			print tag + " not found"
		
	def remove_tag(self, tag):
		try:
			temp_tags = self.tag_list()
			temp_tags.remove(tag)
			self.tags = " ".join(temp_tags)
		except ValueError:
			print tag + " not found"
	
	def rate(self, value):
		self.num_ratings += 1
		self.difficulty = float(self.difficulty*(self.num_ratings-1) + value) / float(self.num_ratings)
	
	def __str__(self):
		return self.name
		
	def save(self, *args, **kwargs):
		if not self.submitted:
			self.submitted = datetime.datetime.now()
			
		super(Problem, self).save(*args, **kwargs)
	
	
	
# tagging.register(Problem)
