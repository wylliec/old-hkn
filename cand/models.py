from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
import nice_types.semester
from nice_types.db import QuerySetManager, PickleField

from request.models import Request
from hkn.info.models import Person, Position
from photologue.models import Photo
from course.models import Klass

class EligibilityListEntryManager(QuerySetManager):
    def for_current_semester(self, *args, **kwargs):
        return self.get_query_set().for_current_semester(*args, **kwargs)

class EligibilityListEntry(models.Model):
    objects = EligibilityListEntryManager()
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=10)
    major = models.CharField(max_length=10)
    email_address = models.EmailField(max_length=100)
    local_street1 = models.CharField(max_length=200)
    local_street2 = models.CharField(max_length=200)
    local_city = models.CharField(max_length=100)
    local_state = models.CharField(max_length=30)
    local_zip = models.CharField(max_length=30)
    class_level = models.CharField(max_length=30)
    semester = nice_types.semester.SemesterField()

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class QuerySet(QuerySet):
        def for_current_semester(self):
            return self.filter(semester=nice_types.semester.current_semester())

CATEGORIES = (("CANDIDATE", "Candidate"), ("MAYBE_CAND", "Maybe candidate"), ("MAYBE_MEMBER", "Maybe member"), ("MEMBER", "Member"), ("UNKNOWN", "Unknown"))
class ProcessedEligibilityListEntry(models.Model):
    entry = models.OneToOneField(EligibilityListEntry)
    person = models.ForeignKey(Person, null=True)
    category = models.CharField(choices=CATEGORIES, max_length=30)

    def __str__(self):
        return "%s %s [%s]" % (self.entry.first_name, self.entry.last_name, self.category)


class CandidateInfo(models.Model):
    """
    CandidateInfo contains auxillary information on a Person's candidacy. Includes candidate_semester, candidate_committee,
    and an initiation_comment set by the VP upon initiation (to record e.g., Person was recipient of Candidate of Semester award)

    Note that actual initiation information is not stored in this object. Look at Person.member_type to determine whether this
    person successfully initiated (or call person.is_initiated())
    """

    person = models.OneToOneField(Person, primary_key = True)
    """A reference to a L{Person} object. To get a handle of the associated Person, do::
        >>>> candidateinfo.person"""

    candidate_semester = nice_types.semester.SemesterField()
    """ The person's candidate semester. """

    candidate_committee = models.ForeignKey(Position, null=True)
    """ The person's candidate committee. """    

    initiated = models.BooleanField()
    """ whether this person initiated in the semester indicated by candidate_semester """

    initiation_comment = models.TextField()
    """ a comment that can be set at initiation time by the VP """

    candidate_picture = models.ForeignKey(Photo, null=True)
    """ candidate picture """
    
    #surveys = models.ManyToManyField(CourseSurvey, related_name="surveyors")
    """ surveyed courses """

    completed_quiz = models.BooleanField()

    completed_surveys = models.BooleanField()

    def save_candidate_picture(self, content, ext=".gif", save=True):
        uname = self.person.username
        self.candidate_picture, created = Photo.objects.get_or_create(title="%s Candidate Picture" % uname, is_public=False)
        self.candidate_picture.image.save(uname + ext, content)
        if save:
            self.save()

    def __unicode__(self):
        return "%s %s %s" % (self.person.name, self.candidate_committee, self.candidate_semester)

class CandidateApplication(models.Model):
    candidateinfo = models.OneToOneField(CandidateInfo)

    transfer_college = models.CharField(null=True, max_length=100)
    committees = PickleField()
    questions = PickleField()
    release_information = models.BooleanField()


# CHALLENGE_PENDING = Null
# CHALLENGE_COMPLETED = True
# CHALLENGE_REJECTED = False

class Challenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    requests = generic.GenericRelation(Request)

    status = models.NullBooleanField()

    candidate = models.ForeignKey(Person, related_name="mychallenges")
    officer = models.ForeignKey(Person, related_name="challenge_requests")


    def get_status_string(self):
        if status:
            return "Confirmed"
        else:
            if status == null:
                return "Pending"
            else:
                return "Rejected"
    
    def get_status_class(self):
        if status:
            return "checklist_done"
        else:
            if status == null:
                return "checklist_in_progress"
            else:
                return "checklist_not_done"

    def save(self, *args, **kwargs):
        # 
        # Check if the officer is a fogie/officer
        # Send a request to the officer that gave the challenge
        # set to pending
        #
        if self.officer.get_member_status < 20:
            print "This person is not an officer or fogie"
            return

        #request.utils.request_confirmation(self, self.candidate, permission_user=self.officer)
        super(Challenge, self).save(*args, **kwargs)
    
class CandidateQuiz(models.Model):
    candidateinfo = models.OneToOneField(CandidateInfo)
    q1 = models.CharField(max_length=100)
    q2 = models.CharField(max_length=100)
    q3 = models.CharField(max_length=100)
    q4 = models.CharField(max_length=100)
    q51 = models.CharField(max_length=100)
    q52 = models.CharField(max_length=100)
    q6 = models.CharField(max_length=100)
    q71 = models.CharField(max_length=100)
    q72 = models.CharField(max_length=100)
    q73 = models.CharField(max_length=100)
    q74 = models.CharField(max_length=100)
    q75 = models.CharField(max_length=100)
    q76 = models.CharField(max_length=100)
    q81 = models.CharField(max_length=100)
    q82 = models.CharField(max_length=100)
    q83 = models.CharField(max_length=100)
    q84 = models.CharField(max_length=100)
    q91 = models.CharField(max_length=100)
    q92 = models.CharField(max_length=100)
    q101 = models.CharField(max_length=100)
    q102 = models.CharField(max_length=100)
    q11 = models.CharField(max_length=100)
    
    q1b = models.BooleanField()
    q2b = models.BooleanField()
    q3b = models.BooleanField()
    q4b = models.BooleanField()
    q5b = models.BooleanField()
    q6b = models.BooleanField()
    q7b = models.BooleanField()
    q8b = models.BooleanField()
    q9b = models.BooleanField()
    q10b = models.BooleanField()
    q11b = models.BooleanField()

    score = models.FloatField()

class CourseSurvey(models.Model):
    """
    This represents the link between a person and a klass s/he will survey. It is one-to-one.
    """
    status = models.NullBooleanField()
    surveyor = models.ForeignKey(CandidateInfo)
    klass = models.ForeignKey(Klass)

# DON'T MOVE THIS IMPORT LINE HIGHER UP BECAUSE IT DEPENDS ON CLASSES DEFINED ABOVE
from hkn.cand.admin import *
import hkn.cand.challenge_requests
import hkn.cand.survey_requests
