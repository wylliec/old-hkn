from django.db import models
from hkn.course.constants import SEMESTER, EXAMS_PREFERENCE, DEPT_ABBR_OVERRIDE, DEPT_ABBR_CORRECT

class CourseManager(models.Manager):
    def query(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
            
        dept_abbr = None
        coursenumber = None
        if query.find(" ") == -1:
            for i, c in enumerate(query):
                if c.isdigit():
                    dept_abbr = query[:i]
                    coursenumber = query[i:]
                    break
                else:
                    dept_abbr = query  
        else:
            (dept_abbr, coursenumber) = query.split(" ")
    
        dept_abbr = Department.proper_abbr(dept_abbr)
    
    #print dept_abbr
    #print coursenumber
    
        objects = objects.filter(department_abbr__iexact = dept_abbr)        
        if coursenumber:
            objects = objects.filter(number__icontains = coursenumber)    
        return objects
    
    def query_exact(self, dept_abbr, coursenumber, objects = None):
        if objects == None:
            objects = self.get_query_set()
            
        dept_abbr = Department.proper_abbr(dept_abbr)
        return objects.filter(department_abbr__iexact = dept_abbr, number__iexact = coursenumber)


# Create your models here.
class Department(models.Model):
    """ Models one of the academic departments. """
    
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 150, unique = True)
    """ Department name: Electrical Engineering, Physics, etc."""
    
    abbr = models.CharField(max_length = 10, unique = True)
    """ Department abbreviation: EE, PHYS, MATH, etc."""
    
    def __str__(self):
        return self.name
    
    """ replaces COMPSCI (correct abbreviation) with CS (common abbreviation) and the like """
    def nice_abbr(abbr):
        return DEPT_ABBR_OVERRIDE[abbr.upper()] or abbr
    nice_abbr = staticmethod(nice_abbr)
    
    def my_nice_abbr(self):
        return Department.nice_abbr(self.abbr)
    
    """ replaces CS (common abbreviation) with COMPSCI (correct abbreviation) and the like """
    def proper_abbr(abbr):
        return DEPT_ABBR_CORRECT[abbr.upper()] or abbr
    proper_abbr = staticmethod(proper_abbr)

    
class Course(models.Model):
    """ Models a course (not to be confused with a klass, which is the teaching of a course in a particular semester"""
    objects = courses = CourseManager()
    
    
    id = models.AutoField(primary_key = True)
    
    department = models.ForeignKey(Department)
    """ The department in charge of the course """
    
    department_abbr = models.CharField(max_length = 10)
    """ cached so we can get the course name (which relies on department abbr) without joining """
    
    number = models.CharField(max_length = 10)
    """ The course number. Note that this isn't really a number, can contain letters e.g. 61A"""
    
    name = models.CharField(max_length = 100)
    """ The course name, e.g. "Structure and Interpretation of Computer Programs" """
    
    description = models.TextField()
    """ A description of the course """
    
    def unprefixed_number(self):
        """
        moves honors and cross-listed prefixes to end of number
        """
        ret = self.number
        if ret[0].lower() in ('h', 'c'):
            ret = ret[1:] + ret[0]
        return ret
    
    def __str__(self):
        return "%s%s: %s" % (Department.nice_abbr(self.department_abbr), self.number, self.name)
    
    def short_name(self, space = False):
        if space:
            return "%s %s" % (Department.nice_abbr(self.department_abbr), self.number)
        else:
            return "%s%s" % (Department.nice_abbr(self.department_abbr), self.number)
    
    def __cmp__(self, other):
        return cmp(self.department_abbr,
                   other.department_abbr) or cmp(self.unprefixed_number(),
                                                 other.unprefixed_number())
    
    class Meta:
        unique_together = (("department", "number"),)
        
    
class Season(models.Model):
    """ Models a season, i.e. fall, spring, or summer """
    
    id = models.AutoField(primary_key = True)
    
    name = models.CharField(max_length = 10)
    """ The name of the season: fall, spring, or summer"""
    
    order = models.IntegerField()
    """ The order of the season. Spring comes before summer which comes before fall """
    
    def __str__(self):
        return self.name
    
    
class Klass(models.Model):
    id = models.AutoField(primary_key = True)
    
    course = models.ForeignKey(Course)
    """ The course that this klass is a particular instance of """
    
    season = models.ForeignKey(Season)
    """ The season this klass was taught """
    
    year = models.DateField()
    """ The year this klass was taught """
    
    section = models.CharField(max_length = 10)
    """ 
    The section number of this klass. 
    
    Differentiates multiple teachings of the same course in the same semester
    (i.e. two physics 7A lectures in the same semester, or lots of 194 sections, etc.)
    """
    
    section_type = models.CharField(max_length = 10)
    """
    The section type (LEC, DIS, etc.)
    """
    
    section_note = models.TextField()
    """
    A note for the particular section/klass, used for 194 and 294 series classes to store 
    the title.
    """
    
    website = models.CharField(max_length = 100)
    """ The URL for the klass website """
    
    newsgroup = models.CharField(max_length = 100)
    """ The klass newsgroup """
    
    def semester(self):
        return (str(self.season) + str(self.year.year))
    
    def __str__(self):
        return "%s %s" % (str(self.course.short_name()), self.semester())
    
    
class Instructor(models.Model):
    """ Models an instructor. """
    
    id = models.AutoField(primary_key = True)
    
    department = models.ForeignKey(Department)
    """ Department to which this instructor belongs """
    
    first = models.CharField(max_length = 30)
    """ Instructor's first name """
    
    middle = models.CharField(max_length = 30)
    """ Instructor's middle name """
    
    last = models.CharField(max_length = 30)
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
