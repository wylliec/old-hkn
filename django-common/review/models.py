from django.db import models
import tagging
from tagging import fields
from tagging.models import Tag

FILE_UPLOAD_DIR =  'review'

class Problem(models.Model):
	
	name = models.CharField(max_length = 30)
	description = models.TextField(blank = True)
	tags = fields.TagField(blank = True)
	difficulty = models.IntegerField(null = True, blank = True)
	question = models.FileField(null = True, upload_to = FILE_UPLOAD_DIR)
	answer = models.FileField(null = True, upload_to = FILE_UPLOAD_DIR)
	
	def tag_list(self):
		return tagging.utils.parse_tag_input(self.tags)
	
		
	def tag_objects(self):
		return Tag.objects.usage_for_model(Problem, filters={'pk':self.id})
	
	def __str__(self):
		return self.name
		
# tagging.register(Problem)