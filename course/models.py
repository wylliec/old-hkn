from django.db import models
from hkn.course.constants import SEMESTER, EXAMS_PREFERENCE

# Create your models here.
class Department(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(maxlength = 75)
    abbr = models.CharField(maxlength = 10)
    
class Course(models.Model):
    id = models.AutoField(primary_key = True)
    department = models.ForeignKey(Department)
    number = models.CharField(maxlength = 10)
    name = models.CharField(maxlength = 100)
    description = models.TextField()
    
class Season(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(maxlength = 10)
    order = models.IntegerField()
    
    
class Klass(models.Model):
    id = models.AutoField(primary_key = True)
    course = models.ForeignKey(Course)
    semester = models.ForeignKey(Season)
    year = models.DateField()
    section = models.CharField(maxlength = 5)
    website = models.CharField(maxlength = 100)
    newsgroup = models.CharField(maxlength = 100)
    
class Instructor(models.Model):
    id = models.AutoField(primary_key = True)
    first = models.CharField(maxlength = 30)
    last = models.CharField(maxlength = 30)
    email = models.EmailField()
    exams_preference = models.IntegerField(choices = EXAMS_PREFERENCE.choices())
    klasses = models.ManyToManyField(Klass)



