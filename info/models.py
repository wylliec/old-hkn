from django.db import models
from django.db.models import Q
from utils import normalizeEmail, normalizeCommitteeName
from hkn import semester
from hkn.info.constants import MEMBER_TYPE
from hkn.settings import IMAGES_PATH
import os

class PeopleManager(models.Manager):
    def from_email(self, email):
        email = normalizeEmail(email)
        return self.get_query_set().get(Q(school_email__iexact = email) | Q(preferred_email__iexact = email))

    def email_contains(self, email):
        email = normalizeEmail(email)
        return self.get_query_set().filter(Q(school_email__icontains = email) | Q(preferred_email__icontains = email))
    

    def query(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
            

        persons = objects
        if query and len(query.strip()) != 0:
            for q in query.split(" "):
                if len(q.strip()) == 0:
                    continue
                persons = persons.filter(Q(first__icontains = q) | Q(last__icontains = q) | Q(user__username__icontains = q))
        return persons
        


class CandidateManager(PeopleManager):
    def get_query_set(self):
        return super(CandidateManager, self).get_query_set().filter(candidateinfo__candidate_semester = semester.getCurrentSemester())

class OfficerManager(PeopleManager):
    def get_query_set(self):
        return super(OfficerManager, self).get_query_set().filter(member_status = MEMBER_TYPE.OFFICER)

class AllOfficerManager(PeopleManager):
    def get_query_set(self):
        return super(AllOfficerManager, self).get_query_set().filter(member_status__gte = MEMBER_TYPE.FOGIE)

class MemberManager(PeopleManager):
    def get_query_set(self):
        return super(MemberManager, self).get_query_set().filter(member_status__gte = MEMBER_TYPE.MEMBER)

class PositionManager(models.Manager):
    def getPosition(self, com_name):
        com_name = normalizeCommitteeName(com_name)
        return super(PositionManager, self).get_query_set().get(short_name = com_name)

class Position(models.Model):
    """
    The Position class represents a particular HKN position: pres, vp, rsec, indrel, compserv, etc. etc.
    
    Each Position has associated with it a "short_name" (i.e. indrel) and a "long_name" (i.e. Industrial Relations).
    """
    
    
    positions = objects = PositionManager()
    """
    PositionManager that provides utility functions, e.g.::
            >>>> position = Position.{position | objects}.getPosition("pres")
            >>>> position = Position.{position | objects}.getPosition("president")
    """
    
    
    
    position_id = models.AutoField(primary_key = True)
    
    short_name = models.CharField(max_length=15)
    """
    Corresponds to usual HKN-name for positions (which is also usually the mailing list names)
    e.g. act, compserv, pres, vp, etc.
    """

    long_name = models.CharField(max_length=50)
    """
    A longer name, e.g. Industrial Relations, Computer Services
    """

    def __str__(self):
        return "%s (%s)" % (self.long_name, self.short_name)


# Create your models here.
class Person(models.Model):
    """
    On its own, the Person class holds general information on people, including their name, email, hkn member status,
    and positions held.

    More importantly, the Person class can be used to access other classes: L{ExtendedInfo}, L{CandidateInfo},
    L{Officership}, L{RSVP}, L{User <auth.User>}

    For many of these object, there is a one-to-one correspondence between Person and e.g., ExtendedInfo. To retrieve
    a Person's associated ExtendedInfo and User::
        >>>> from hkn.info.models import Person
        >>>> some_person = Person.members.get(first = "Hisham")
        >>>> moreinfo = some_person.extendedinfo
        >>>> user = some_person.user

    For other objects for which there are one-to-many correspondences (e.g. each Person can have many RSVPs, but each RSVP
    object has one associated person) you can do the following::
        >>>> rsvps  = some_person.rsvp_set

    For other objects for wmodels.ManyToManyField(Position)hich there are many-to-many correspondences (e.g. each Person has held lots of Positions, but
    each Position can also have many Persons that have occupied that position)::
        >>>> positions = some_person.positions

    To figure out the right name for the related object(extendedinfo, user, rsvp_set) lowercase the class name
    (ExtendedInfo, User, RSVP) and then add '_set' for one-to-many relationships or pluralize for many-to-many relationships.

    If in doubt, get a shell (run './manage.py shell' in your server root) and try the following::
        >>>> from hkn.info.models import Person
        >>>> some_person = Person.members.get(first = "Hisham")
        >>>> dir(some_person)

    This will give you all of the attributed and functions of the Person, so look through the attributes and try them out.
    """
    

    people = objects = PeopleManager()
    """
    This is an object manager that retrieves ALL people known to HKN (you can refer to it
    it as either Person.objects or Person.people). e.g.::
            >>>> all_people_ever = Person.{people | objects}.all()
            >>>> hisham = Person.{people | objects}.get(first = "Hisham")

    This object manager (and all the ones that follow for the Person class) have
    some utility methods defined on them that make certain lookups easier, i.e.::
            >>>> some_person = Person.{people | objects}.email_contains("hzarka")

    Look at the docs for the Manager to see the available methods.
    """       


    candidates = CandidateManager()
    """
    An object manager that filters to only current candidates::
        >>>> candidate_named_james = Person.candidates.get(first = "James")

    Note that the notion of "current candidate" here is defined by People whose associated
    CandidateInfo.candidate_semester is equal to the current semester. This does NOT
    go by the member_type field in the Person class, because at the end of the semester
    when the VP starts initiating candidates the member_type field will be updated but
    we shouldn't consider the candidates as having initiated until the next semester begins.
    """


    officers = OfficerManager()
    """
    Same as above, but only current officers.
    """


    fogies = exofficers = all_officers = AllOfficerManager()
    """
    Same as above, but all officers ever.
    """

    members = MemberManager()
    """
    Same as above, but all initiated members.
    """

    id = models.AutoField(primary_key = True)


    first = models.CharField(max_length = 30)
    """ Person's first name (sometimes preferred name, see L{realfirst})"""


    last = models.CharField(max_length=30)
    """ Person's last name """
    

    realfirst = models.CharField(max_length=30)
    """ 
    Real first name (the Person's official name, if it isn't already in L{first}).
    Can be empty if the Person's first name is their official name
    """
    

    school_email = models.EmailField()
    """ 
    Person's official school email address. Probably a bad idea to issue lookup queries on this,
    see the object managers for some utility functions to help out with this 
    """
    

    preferred_email = models.EmailField()
    """ 
    Person's preferred email address, where email should go. Probably a bad idea to issue lookup 
    queries on this (since sometimes we only have school_email, see the object managers for some 
    utility functions to help out with this 
    """
    

    positions = models.ManyToManyField(Position)
    """ A list of officership positions (i.e. not candidate committee) that this Person has held in the past. """


    member_status = models.IntegerField()
    """ The person's member status. See L{hkn.info.constants.MEMBER_TYPE} for some more details. """
    


    def __str__(self):
        return "%s %s %s (%s)" % (str(self.id), self.first, self.last, self.email() )

    def email(self):
        """
        Returns a person's preferred email if available, and school email otherwise.
        """
        if len(self.preferred_email) > 0:
            return self.preferred_email
        return self.school_email

    def name(self):
        """
        Returns the person's full name (first + last).
        """
        return self.first + " " + self.last

    def picture_url(self):
        semester = self.candidateinfo.candidate_semester
        pic_url = "candidate_images/" + semester + "/normal/" + self.first + "_" + self.last + ".JPG"
        if not os.path.exists(os.path.join(IMAGES_PATH, pic_url)):
            return "/images/candidate_images/thumbnails/default.JPG"
        return "/images/" + pic_url

    def thumbnail_url(self):
        if self.member_status >= 4 and self.has_officer_pic():
            return self.officer_url()
        semester = self.candidateinfo.candidate_semester
        thumb_url = "candidate_images/" + semester + "/thumbnails/" + self.first + "_" + self.last + ".JPG"
        if not os.path.exists(os.path.join(IMAGES_PATH, thumb_url)):
            return "/images/candidate_images/thumbnails/default.JPG"
        return "/images/" + thumb_url

    def officer_url(self):
        un = self.user.username
        url1 = "officerpics/" + un + ".jpg"
        url2 = "officerpics/" + un + ".gif"
        if os.path.exists(os.path.join(IMAGES_PATH, url1)):
            return "/images/" + url1
        if os.path.exists(os.path.join(IMAGES_PATH, url2)):
            return "/images/" + url2
        return "/images/officerpics/lion.jpg"

    def has_officer_pic(self):
        un = self.user.username
        url1 = "officerpics/" + un + ".jpg"
        url2 = "officerpics/" + un + ".gif"
        if os.path.exists(os.path.join(IMAGES_PATH, url1)):
            return True
        if os.path.exists(os.path.join(IMAGES_PATH, url2)):
            return True
        return False

    def is_initiated(self):
        """
        Predicate: was this person ever initiated? (i.e. are they a member)

        @rtype: boolean
        @return: whether this person is a member
        """
        return self.candidateinfo.initiated

    def initiate(self, initiate = True):
        """
        Initiates the person. Sets their MEMBER_TYPE to Member or Candidate as appropriate.

        @type initiate: boolean
        @param initiate: True to set MEMBER_TYPE to Member, False for Candidate
        """
        if initiate:
            self.member_status = MEMBER_TYPE.MEMBER
        else:
            self.member_status = MEMBER_TYPE.CANDIDATE

    class Meta:
        ordering = ["first", "last"]

class ExtendedInfo(models.Model):
    """
    ExtendedInfo for a Person, so that we don't have to store all of this information along with the main Person class.

    Due to incomplete records from semesters past, not all of this information may be present for many people, so be sure
    to sanity check!
    """
        

    person = models.OneToOneField(Person, primary_key = True)
    """A reference to a L{Person} object. To get a handle of the associated Person, do::
        >>>> extendedinfo.person"""
    

    sid = models.CharField(max_length=10)
    """ The person's SID. Try to use this as little as possible, will be phased out gradually. """
    

    grad_semester = models.CharField(max_length=5)
    """ The person's graduation semester. Usually taken at initiation time, so subject to change. """
    

    local_phone = models.CharField(max_length=20)
    """ Local phone number, usually cell phone. """
    

    perm_phone = models.CharField(max_length=20)
    """ Permanent phone number, usually home phone (?) """
    

    local_addr = models.CharField(max_length=100)
    """ Local address """
    

    perm_addr = models.CharField(max_length=100)
    """ Permanent (home) address """

    def __str__(self):
        return "%s %s %s (%s)" % (self.person.first, self.person.last, self.sid, self.get_phone() )

    def get_phone(self):
        """
        Gets a formatted version of local_phone if available and perm_phone otherwise.

        Format is (###) ###-####

        @rtype: string
        @return: their local phone number if on file, permanent otherwise.
        """
                

        if self.local_phone is not None and len(self.local_phone) > 0:
            return self.format_phone(self.local_phone)
        return self.format_phone(self.perm_phone)
    

    def format_phone(self, phone):
        """ Helper function for the above. """
        if len(phone) == 10:
            return "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]
        else:
            return phone

    class Admin:
        pass

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
    

    candidate_semester = models.CharField(max_length=5)
    """ The person's candidate semester. """
    

    candidate_committee = models.ForeignKey(Position)
    """ The person's candidate committee. """
    

    initiated = models.BooleanField()
    """ whether this person initiated this semester """
    

    initiation_comment = models.TextField()
    """ a comment that can be set at initiation time by the VP """

    def __str__(self):
        return "%s %s (%s)" % (self.candidate_committee.short_name, self.candidate_semester, self.initiation_comment)
            



class Officership(models.Model):
    """
    The official record of Officership in HKN. Brings together a L{Person}, L{Position}, and L{semester}.

    If Lahini Arunachalam was VP in fa07, then the corresponding officership object would have
    person = Lahini, position = vp, semester = fa07
    """
        

    officership_id = models.AutoField(primary_key = True)
    semester = models.CharField(max_length=5)
    """The L{semester} of this officership."""
    

    position = models.ForeignKey(Position)
    """
    A reference to a L{Position} object. To get the handle of the associated Position, do::
        >>>> officership_object.position
    """	
    

    person = models.ForeignKey(Person)
    """
    A reference to a L{Person} object. To get the handle of the associated Person, do::
        >>>> officership_object.person
    """

    def __str__(self):
        return "%s %s %s %s" % (self.semester, self.position.short_name, self.person.first, self.person.last)
