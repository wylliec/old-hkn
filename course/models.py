from django.db import models
from hkn.course.constants import SEMESTER, EXAMS_PREFERENCE

# Create your models here.
class Department(models.Model):
    """ Models one of the academic departments. """
    
    id = models.AutoField(primary_key = True)
    name = models.CharField(maxlength = 75)
    """ Department name: Electrical Engineering, Physics, etc."""
    
    abbr = models.CharField(maxlength = 10)
    """ Department abbreviation: EE, PHYS, MATH, etc."""
    
class Course(models.Model):
    """ Models a course (not to be confused with a klass, which is the teaching of a course in a particular semester"""
    
    id = models.AutoField(primary_key = True)
    department = models.ForeignKey(Department)
    """ The department in charge of the course """
    
    number = models.CharField(maxlength = 10)
    """ The course number. Note that this isn't really a number, can contain letters e.g. 61A"""
    
    name = models.CharField(maxlength = 100)
    """ The course name, e.g. "Structure and Interpretation of Computer Programs" """
    
    description = models.TextField()
    """ A description of the course """
    
class Season(models.Model):
    """ Models a season, i.e. fall, spring, or summer """
    
    id = models.AutoField(primary_key = True)
    name = models.CharField(maxlength = 10)
    """ The name of the season: fall, spring, or summer"""
    
    order = models.IntegerField()
    """ The order of the season. Spring comes before summer which comes before fall """
    
    
class Klass(models.Model):
    id = models.AutoField(primary_key = True)
    course = models.ForeignKey(Course)
    """ The course that this klass is a particular instance of """
    
    season = models.ForeignKey(Season)
    """ The season this klass was taught """
    
    year = models.DateField()
    """ The year this klass was taught """
    
    section = models.CharField(maxlength = 5)
    """ 
    The section number of this klass. 
    
    Differentiates multiple teachings of the same course in the same semester
    (i.e. two physics 7A lectures in the same semester, or lots of 194 sections, etc.)
    """
    
    section_title = models.CharField(maxlength = 50)
    """
    A title for the particular section, useful for 194 and 294 series classes where each
    section is very different.
    """
    
    website = models.CharField(maxlength = 100)
    """ The URL for the klass website """
    
    newsgroup = models.CharField(maxlength = 100)
    """ The klass newsgroup """
    
    
class Instructor(models.Model):
    """ Models an instructor. """
    
    id = models.AutoField(primary_key = True)
    
    first = models.CharField(maxlength = 30)
    """ Instructor's first name """
    
    last = models.CharField(maxlength = 30)
    """ Instructor's last name """
    
    email = models.EmailField()
    """ Instructor's email address """
    
    exams_preference = models.IntegerField(choices = EXAMS_PREFERENCE.choices())
    """ 
    Instructor's exam preference. Can be set to indicate that the professor would
    never wants his exams posted, always wants his exams posted, or that we should
    always ask before posting his exams
    """
    
    klasses = models.ManyToManyField(Klass)
    """
    A many-to-many relationship of the klasses taught by the instructor.
    """



