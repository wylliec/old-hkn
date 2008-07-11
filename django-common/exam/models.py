import datetime, re, os, string

#from django.contrib.auth.models import User
from django.contrib.auth.models import User

from course.models import *
from constants import FILE_UPLOAD_DIR, EXAM_TYPE


from django import db


class ExamManager(db.models.Manager):
    def query_course(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
            
        (dept_abbr, coursenumber) = Course.objects.parse_query(query)
        if dept_abbr:
            objects = objects.filter(klass__course__department_abbr__iexact = dept_abbr)        
        if coursenumber:
            objects = objects.filter(klass__course__number__iexact = coursenumber)    
        
        return objects
    
    def query_instructor(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
        
        (last, first, dd) = Instructor.objects.parse_query(query)

        if first and last:
            objects = objects.filter(klass__instructor__first__icontains = first, klass__instructor__last__icontains = last)
        elif last:
            objects = objects.filter(klass__instructor__last__icontains = last)
        
        return objects
        
        
            
        
def get_semester_start(sem):
    """
    Gets the start time of the semester, assumed to be in ssyy format.
    Defaults to current semester.


    @type sem:  string
    @param sem: the semester, or current semester if not specified
    @rtype: datetime
    @return: a datetime representing the beginning of the semester
    """
    s = sem[0:2]
    y = "20" + sem[2:4]
    if s == "fa":
        return datetime.datetime(string.atoi(y), 8, 1)
    elif s == "su":
        return datetime.datetime(string.atoi(y), 6, 1)
    else:
        return datetime.datetime(string.atoi(y), 1, 1)


class Exam(db.models.Model):
    """ Models an exam. """
    
    objects = ExamManager()
    
    id = db.models.AutoField(primary_key = True)
    
    klass = db.models.ForeignKey(Klass)
    """ The particular klass in which the exam was given. """
    
    course = db.models.ForeignKey(Course)
    """ The course this exam is for (cached) """
    
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
    
    def get_exam_description(self):
        solutions = ""
        if self.is_solution:
            solutions = "[Solutions]"
        if self.number and self.number >= 1:
            return "%s %d %s" % (EXAM_TYPE[self.exam_type], self.number, solutions)
        else:
            return "%s %s" % (EXAM_TYPE[self.exam_type], solutions)
        
    def get_exam_format(self):
        return os.path.splitext(self.get_file_filename())[1]
    
    def get_exam_filename(self):
        return ("%s_%s_%s_%s%d" % (self.klass.course.short_name(), self.klass.semester(), self.klass.section, self.exam_type, self.number or 0)).replace(" ", "-")
    
    def auto_exam_date(self):
        semester_start_date = get_semester_start(self.klass.semester())
        weights = {EXAM_TYPE.MIDTERM : 7, EXAM_TYPE.QUIZ : 1, EXAM_TYPE.FINAL : 30, EXAM_TYPE.REVIEW : 29}
        if self.number:
            days_delta = (1 + self.number) * weights[self.exam_type]
        else:
            days_delta = weights[self.exam_type]
        return semester_start_date + datetime.timedelta(days = days_delta)
    
    def save(self):
        if self.klass_id:
            self.exam_date = self.auto_exam_date()
        if self.course_id == None:
            self.course = self.klass.course
        if not self.submitted:
            self.submitted = datetime.datetime.now()
        super(Exam, self).save()

    class Admin:
        list_filter = ['exam_type']
