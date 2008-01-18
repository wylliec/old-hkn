#tutoring models
from django.db import models
from hkn.course import models as courses
from hkn.info.models import Person
from hkn.tutor.constants import *

# Create your models here.

#Models pertaining to tutoring signups

class Availability(models.Model):
    """ Models a person's time and office availability for a given season/year. """
    
    person = models.ForeignKey(Person)
    slot = models.CharField(maxlength = 30)
    office = models.CharField(maxlength = 5, choices = (OFFICE_CHOICES)) #Soda or Cory
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    preference = models.IntegerField()

    def atCory(self):
        return self.office == "Cory"
    def atSoda(self):
        return self.office == "Soda"
    
class Assignment(models.Model):
    """ Models when a person will tutor for a given season/year and schedule version. """
    
    person = models.ForeignKey(Person)
    slot = models.CharField(maxlength = 30)
    office = models.CharField(maxlength = 5, choices = (OFFICE_CHOICES)) #Soda or Cory
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    
    version = models.PositiveIntegerField()
    """
    Allows multiple schedule versions to be generated and saved
    for a single season/year.
    """

    def atCory(self):
        return self.office == "Cory"
    def atSoda(self):
        return self.office == "Soda"

class CanTutor(models.Model):
    """ Models who can tutor what for a particular season/year. """
    
    person = models.ForeignKey(Person)
    course = models.ForeignKey(courses.Course)
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    


#Models pertaining to tutoring attendance

class Attendance(models.Model):
    """ Models one of the academic departments. """
    
    person = models.ForeignKey(Person)
    """ TODO: need to auto-assign to "Anonymous" person when blank """
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    repeat = models.BooleanField()
    """ If we are certain that a tutee has come before, set repeat to true """
    
class CourseTutored(models.Model):
    """ Models a course tutored to a tutee during a particular attendance """
    attendance = models.ForeignKey(Attendance)
    course = models.ForeignKey(courses.Course)
    topics = models.CharField(maxlength = 150)
    """ Description of topics tutored """