from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
import nice_types.semester
from nice_types.db import QuerySetManager, PickleField

from request.models import Request
from hkn.info.models import Person, Position
from photologue.models import Photo

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

    def save_candidate_picture(self, content, ext=".gif", save=True):
        uname = self.person.username
        self.candidate_picture, created = Photo.objects.get_or_create(title="%s Candidate Picture" % uname, is_public=False)
        self.candidate_picture.image.save(uname + ext, content)
        if save:
            self.save()

    def __unicode__(self):
        return "%s %s %s" % (self.person.name, self.candidate_committee, self.candidate_semester)

class CandidateApplication(models.Model):
    entry = models.ForeignKey(EligibilityListEntry)
    candidateinfo = models.ForeignKey(CandidateInfo)

    transfer_college = models.CharField(null=True, max_length=100)
    committees = PickleField()
    questions = PickleField()


# CHALLENGE_PENDING = Null
# CHALLENGE_COMPLETED = True
# CHALLENGE_REJECTED = False

class Challenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    requests = generic.GenericRelation(Request)

    status = models.NullBooleanField()
    #candidate_id = models.IntegerField()
    #officer_id = models.IntegerField()

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
        
           
            
from hkn.cand.admin import *
import hkn.cand.challenge_requests
