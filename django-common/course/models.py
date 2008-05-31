from django.db import models
from constants import SEMESTER, EXAMS_PREFERENCE, DEPT_ABBR_OVERRIDE, DEPT_ABBR_CORRECT
import re

class CourseManager(models.Manager):    
    course_patterns = (
                     re.compile(r'(?P<dept>\w*)\s*(?P<course>\w*)'),  # matches "CS 61A"
                     re.compile(r'(?P<dept>[A-Za-z]+)(?P<course>\d\w*)'),  # matches "CS61A"
                     re.compile(r'(?P<dept>\w+)'),  # matches "CS"
                     )    
    def parse_query(self, query):
        for course_pattern in CourseManager.course_patterns:
            m = course_pattern.match(query)
            if m:
                return (Department.proper_abbr(m.groupdict().get("dept")), m.groupdict().get("course"))
            
        return (None, None)
    
    def query(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
            

        (dept_abbr, coursenumber) = self.parse_query(query)
    
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
        if abbr:
            return DEPT_ABBR_CORRECT.get(abbr.upper(), abbr.upper())
        return None
    proper_abbr = staticmethod(proper_abbr)

    class Admin:
        pass

    
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
    
    name = models.CharField(max_length = 150)
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

    def short_name_space(self):
        return self.short_name(True)
    
    def __cmp__(self, other):
        return cmp(self.department_abbr,
                   other.department_abbr) or cmp(self.unprefixed_number(),
                                                 other.unprefixed_number())
    
    class Meta:
        unique_together = (("department", "number"),)
        
    class Admin:
        pass
    
class Season(models.Model):
    """ Models a season, i.e. fall, spring, or summer """
    
    id = models.AutoField(primary_key = True)
    
    name = models.CharField(max_length = 10)
    """ The name of the season: fall, spring, or summer"""
    
    order = models.IntegerField()
    """ The order of the season. Spring comes before summer which comes before fall """
    
    def __str__(self):
        return self.name
    
    def abbr(self):
        return self.name[:2]
    
    class Admin:
        pass
    
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
        return (self.season.abbr() + str(self.year.year)[2:4])

    def pretty_semester(self):
        return "%s %d" % (self.season.name.title(), self.year.year)
    
    def instructors(self):
        last_names = [inst.last for inst in self.instructor_set.all()]
        return ", ".join(last_names)
    
    def __str__(self):
        return "%s %s" % (str(self.course.short_name()), self.semester())

    class Admin:
        pass
    
class InstructorManager(models.Manager):
    
    instructor_patterns = (
                     re.compile(r'(?P<last>\w*),\s*(?P<first>\w*)\s*\[(?P<dept>\w*)\]'),  # matches "Harvey, Brian [CS]"
                     re.compile(r'(?P<last>\w*),\s*(?P<first>\w*)'),                      # matches "Harvey, Brian"
                     re.compile(r'(?P<first>\w*)\s+(?P<last>\w*)'),                      # matches "Brian Harvey"
                     re.compile(r'(?P<last>\w*)'),                      # matches "Harvey"
                     )
    def parse_query(self, query):        
        for instructor_pattern in InstructorManager.instructor_patterns:
            m = instructor_pattern.match(query)
            if m:
                d = m.groupdict()
                return (d.get("last"), d.get("first"), Department.proper_abbr(d.get("dept")))            
        return (None, None, None)
    
    def query(self, query, objects = None, course_query = None, dept_abbr = None, course_number = None, courses = None):
        if objects == None:
            objects = self.get_query_set()
            
        if not (dept_abbr or course_number) and course_query:
            (dept_abbr, course_number) = Course.objects.parse_query(course_query)
        
        if dept_abbr and course_number:
            courses = Course.objects.filter(department_abbr__iexact = dept_abbr, number__icontains = course_number)
        elif dept_abbr:
            courses = Course.objects.filter(department_abbr__iexact = dept_abbr)
        
        (last, first, dd) = self.parse_query(query)

        if first and last:
            objects = objects.filter(last__istartswith = last, first__istartswith = first)
        elif last:
            objects = objects.filter(last__istartswith = last)
        else:
            return Instructor.objects.none()
            
        if courses:
            return objects.filter(klasses__course__in = courses).distinct()
        else:
            return objects

    
class Instructor(models.Model):
    """ Models an instructor. """
    
    objects = InstructorManager()
    
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
    
    def short_name(self, first = False, dept = False):
        if first:
            first = self.first
        else:
            first = self.first[0]
            
            
        if dept:
            return "%s, %s [%s]" % (self.last, first, self.department.my_nice_abbr())
        else:
            return "%s, %s" % (self.last, first)

    class Admin:
        pass
