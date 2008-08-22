import datetime, re, os, string, os.path

from django.contrib.auth.models import User, Permission

from course.models import *
from constants import FILE_UPLOAD_DIR, EXAM_TYPE
import request.utils

from django.db.models.query import QuerySet
from nice_types.db import QuerySetManager
from nice_types.semester import Semester

from django import db



class ExamManager(QuerySetManager):
        def query_course(self, query):                          
            return self.get_query_set().query_course(query)
        
        def query_instructor(self, query):   
            return self.get_query_set().query_instructor(query)    
            
        def after(self, value):
            return self.get_query_set().after(value)  
            
            
class PublishedExamManager(ExamManager):
        def get_query_set(self):
            return super(PublishedExamManager, self).get_query_set().filter(publishable=True)            

class UnpublishedExamManager(ExamManager):
        def get_query_set(self):
            return super(UnpublishedExamManager, self).get_query_set().filter(publishable=False) 


class Exam(db.models.Model):
    """ Models an exam. """
    all = ExamManager()    
    published = PublishedExamManager()
    unpublished = UnpublishedExamManager()
    
    id = db.models.AutoField(primary_key = True)
    
    klass = db.models.ForeignKey(Klass)
    """ The particular klass in which the exam was given. """
    
    course = db.models.ForeignKey(Course)
    """ The course this exam is for (cached) """
    
    department = db.models.ForeignKey(Department)
    """ The department this exam is for (cached) """    
    
    file = db.models.FileField(null = True, upload_to = FILE_UPLOAD_DIR)
    """ The local filesystem path to where the actual exam is stored. """
    
    exam_type = db.models.CharField(choices = EXAM_TYPE.choices(), max_length = 10)
    """ The type of exam (e.g., Midterm, Final). """
    
    number = db.models.IntegerField(blank = True)
    """ The exam number. If unique (i.e., only one final), leave this field blank. """ 
    
    version = db.models.CharField(max_length = 1, blank = True)
    """ The version of the exam. If only one version, leave this field blank. """

    is_solution = db.models.BooleanField()
    """ True if this is the solutions file (i.e., not the original exam). """
    
    paper_only = db.models.BooleanField()
    """ True if HKN has a paper copy but does not have a PDF version. """
    
    publishable = db.models.BooleanField()
    """ True if HKN has permission to post this exam publicly online. """

    topics = db.models.TextField()
    """ A text block of topics relevant to this exam. """
    
    submitter = db.models.ForeignKey(User, null = True)
    """ the person who submitted this exam """
    
    submitted = db.models.DateTimeField()
    """ when this exam was submitted """
    
    exam_date = db.models.DateTimeField()
    """ when the exam was administered. used for sorting """   

    def __str__(self):
        s = "%s %s %s" % (self.klass, self.exam_type, self.number)
        if self.is_solution:
            s += " Solutions"
        if self.publishable:
            s += " (publishable)"
        return s

    def request_confirmation(self):
        return request.utils.request_confirmation(self, self.submitter, Permission.objects.get(codename="add_exam"))
    
    @property
    def integer_number(self):
        return int(self.number)
        
    class QuerySet(QuerySet):
        def query_course(self, query):              
            courses = Course.objects.ft_query(query)
            print courses
            return self.filter(course__in = courses)
        
        def query_instructor(self, query):
            instrs = Instructor.objects.ft_query(query)
            return self.filter(klass__instructors__in = instrs)            
            (last, first, dd) = Instructor.objects.parse_query(query)

            if first and last:
                return self.filter(klass__instructors__first__icontains = first, klass__instructors__last__icontains = last)
            elif last:
                return self.filter(klass__instructors__last__icontains = last)            
            return self
            
        def after(self, value):
            if len(value) != 4:
                return self
            return self.filter(exam_date__gte = Semester(value).start_date)
    
    
    def describe_exam_type(self):
        if self.exam_type == EXAM_TYPE.FINAL:
            return EXAM_TYPE[EXAM_TYPE.FINAL]
        else:
            return "%s %d" % (EXAM_TYPE[self.exam_type], self.number)
                
    def get_exam_description(self, course=False, semester=False, instructors=False):
        description = []
        if course:
            description.append(str(self.course))
            
        if semester:
            description.append(str(self.semester))
            
        description.append(self.describe_exam_type())
        
        if instructors:
            description.append("[%s]" % self.klass.instructor_names())
        
        return " ".join(description)
            
        
    def get_exam_format(self):
        return os.path.splitext(self.file.name)[1].strip(". ")
    
    def get_exam_filename(self):
        return ("%s_%s_%s_%s%d" % (self.klass.course.short_name(), self.klass.semester, self.klass.section, self.exam_type, self.number or 0)).replace(" ", "-")
        
    def get_semester_sort(self):
        return self.klass.semester.start_date
    
    def auto_exam_date(self):
        semester_start_date = self.klass.semester.start_date
        weights = {EXAM_TYPE.MIDTERM : 7, EXAM_TYPE.QUIZ : 1, EXAM_TYPE.FINAL : 30, EXAM_TYPE.REVIEW : 29}
        if self.number:
            days_delta = (1 + self.integer_number) * weights[self.exam_type]
        else:
            days_delta = weights[self.exam_type]
        return semester_start_date + datetime.timedelta(days = days_delta)
    
    def save(self):
        if self.klass_id:
            self.exam_date = self.auto_exam_date()
        if self.course_id == None:
            self.course = self.klass.course
        if self.department_id == None:
            self.department = self.course.department
        if not self.submitted:
            self.submitted = datetime.datetime.now()
        super(Exam, self).save()
        
from admin import *
from requests import *
