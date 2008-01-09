from django.db import models
from hkn.exam.constants import FILE_UPLOAD_DIR, EXAM_TYPE
from hkn.course.models import Klass

# Create your models here.

class Exam(models.Model):
    """ Models an exam. """
    
    id = models.AutoField(primary_key = True)
    klass = models.ForeignKey(Klass)
    """ The particular class in which the exam was given. """
    
    file = models.FileField(upload_to = FILE_UPLOAD_DIR)
    """ The local filesystem path to where the actual exam is stored. """
    
    exam_type = models.CharField(choices = EXAM_TYPE.choices())
    """ The type of exam (e.g., Midterm, Final). """
    
    number = models.IntegerField(blank = True)
    """ The exam number. If unique (i.e., only one final), leave this field blank. """ 
    
    version = models.CharField(maxlength = 1, blank = True)
    """ The version of the exam. If only one version, leave this field blank. """

    is_solution = models.BooleanField()
    """ True if this is the solutions file (i.e., not the original exam). """
    
    paper_only = models.BooleanField()
    """ True if HKN has a paper copy BUT does not have a PDF version. """
    
    publishable = models.BooleanField()
    """ True if HKN has permission to post this exam publicly online. """

    topics = models.TextField()
    """ A text block of topics relevant to this exam. """

%    def __str__(self):
%        return "%s %s %s%s" % self.course
