from django.db import models
from hkn.course.constants import SEMESTER, EXAMS_PREFERENCE

# Create your models here.
class Department(models.Model):
    """ Models one of the academic departments. """
    
    id = models.AutoField(primary_key = True)
    name = models.CharField(maxlength = 75, unique = True)
    """ Department name: Electrical Engineering, Physics, etc."""
    
    abbr = models.CharField(maxlength = 10, unique = True)
    """ Department abbreviation: EE, PHYS, MATH, etc."""
    
    def __str__(self):
            return self.name

    
class Course(models.Model):
    """ Models a course (not to be confused with a klass, which is the teaching of a course in a particular semester"""
    
    id = models.AutoField(primary_key = True)
    
    department = models.ForeignKey(Department)
    """ The department in charge of the course """
    
    department_abbr = models.CharField(maxlength = 10)
    """ cached so we can get the course name (which relies on department abbr) without joining """
    
    number = models.CharField(maxlength = 10)
    """ The course number. Note that this isn't really a number, can contain letters e.g. 61A"""
    
    name = models.CharField(maxlength = 100)
    """ The course name, e.g. "Structure and Interpretation of Computer Programs" """
    
    description = models.TextField()
    """ A description of the course """
    
    def __str__(self):
        return "%s%s: %s" % (self.department_abbr, self.number, self.name)
    
    class Meta:
        unique_together = (("department", "number"),)
        
    
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
    
    section = models.CharField(maxlength = 10)
    """ 
    The section number of this klass. 
    
    Differentiates multiple teachings of the same course in the same semester
    (i.e. two physics 7A lectures in the same semester, or lots of 194 sections, etc.)
    """
    
    section_note = models.TextField()
    """
    A note for the particular section/klass, used for 194 and 294 series classes to store 
    the title.
    """
    
    website = models.CharField(maxlength = 100)
    """ The URL for the klass website """
    
    newsgroup = models.CharField(maxlength = 100)
    """ The klass newsgroup """
    
    
class Instructor(models.Model):
    """ Models an instructor. """
    
    id = models.AutoField(primary_key = True)
    
    department = models.ForeignKey(Department)
    """ Department to which this instructor belongs """
    
    first = models.CharField(maxlength = 30)
    """ Instructor's first name """
    
    middle = models.CharField(maxlength = 30)
    """ Instructor's middle name """
    
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
    
    distinguished_teacher = models.BooleanField()
    """ If this instructor has won the Distinguished Teacher award. """
    
    def __str__(self):
        return "%s %s %s" % (self.first, self.middle, self.last)