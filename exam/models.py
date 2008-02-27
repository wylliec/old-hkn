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
    
    exam_type = models.CharField(choices = EXAM_TYPE.choices(), max_length = 10)
    """ The type of exam (e.g., Midterm, Final). """
    
    number = models.IntegerField(blank = True)
    """ The exam number. If unique (i.e., only one final), leave this field blank. """ 
    
    version = models.CharField(max_length = 1, blank = True)
    """ The version of the exam. If only one version, leave this field blank. """

    is_solution = models.BooleanField()
    """ True if this is the solutions file (i.e., not the original exam). """
    
    paper_only = models.BooleanField()
    """ True if HKN has a paper copy but does not have a PDF version. """
    
    publishable = models.BooleanField()
    """ True if HKN has permission to post this exam publicly online. """

    topics = models.TextField()
    """ A text block of topics relevant to this exam. """

    def __str__(self):
        s = "%s %s %s" % (self.klass, self.exam_type, self.number)
        if self.is_solution:
            s += " Solutions"
        if self.publishable:
            s += " (publishable)"
        return s
    
    def get_exam_filename(self):
        return ("%s_%s_%s_%s%d" % (self.klass.course.short_name(), self.klass.semester(), self.klass.section, self.exam_type, self.number)).replace(" ", "-")
