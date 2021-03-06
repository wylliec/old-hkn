from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


from hkn.info.utils import normalize_email, normalize_committee_name, int_to_base36
from hkn.info.constants import MEMBER_TYPE
from hkn.settings import IMAGES_PATH

from photologue.models import Photo

import nice_types.semester
import os, datetime, types, random

from nice_types.db import QuerySetManager, PickleField
from nice_types import semester

class BlankImage(object):
    def __init__(self):
        self.url = "/static/images/site/lion.gif"

    def __getattr__(self, attr):
        return lambda: self.url

class PeopleManager(QuerySetManager):
        def from_email(self, *args, **kwargs):
            return self.get_query_set().from_email(*args, **kwargs)
            
        def email_contains(self, *args, **kwargs):
            return self.get_query_set().email_contains(*args, **kwargs)
    
        def filter_restricted(self, *args, **kwargs):
            return self.get_query_set().filter_restricted(*args, **kwargs)

        def ft_query(self, *args, **kwargs):
            return self.get_query_set().ft_query(*args, **kwargs)
        
        def create_person(self, first_name, last_name, username, email, member_type, password=None):
            now = datetime.datetime.now()
            email = normalize_email(email)
            person = self.model(first_name=first_name, last_name=last_name, email=email, username=username, password="placeholder", last_login=now, date_joined=now, member_type=member_type, privacy={})
            if email.endswith("@berkeley.edu"):
                person.school_email = email
            if password:
                person.set_password(password)
            else:
                person.set_unusable_password()
            person.save()
            ExtendedInfo.objects.create(person=person, sid="", grad_semester=None, local_addr="", perm_addr="")
            return person

            

class CandidateManager(PeopleManager):
    def get_query_set(self):
        return super(CandidateManager, self).get_query_set().filter(candidateinfo__candidate_semester = nice_types.semester.current_semester().abbr())

class OfficerManager(PeopleManager):
    def get_query_set(self):
        return super(OfficerManager, self).get_query_set().filter(member_type = MEMBER_TYPE.OFFICER)

class AllOfficerManager(PeopleManager):
    def get_query_set(self):
        return super(AllOfficerManager, self).get_query_set().filter(member_type__gte = MEMBER_TYPE.FOGIE)

class MemberManager(PeopleManager):
    def get_query_set(self):
        return super(MemberManager, self).get_query_set().filter(member_type__gte = MEMBER_TYPE.MEMBER)

class ImportedPeopleManager(PeopleManager):
    def get_query_set(self):
        return super(ImportedPeopleManager, self).get_query_set().filter(username__startswith="imported__")


class PositionManager(models.Manager):
    def get_position(self, com_name):
        com_name = normalize_committee_name(com_name)
        return super(PositionManager, self).get_query_set().get(short_name = com_name)

class Position(Group):
    """
    The Position class represents a particular HKN position: pres, vp, rsec, indrel, compserv, etc. etc.
    
    Each Position has associated with it a "short_name" (i.e. indrel) and a "long_name" (i.e. Industrial Relations).
    """
    
    
    positions = objects = PositionManager()
    """
    PositionManager that provides utility functions, e.g.::
            >>>> position = Position.{position | objects}.get_position("pres")
            >>>> position = Position.{position | objects}.get_position("president")
    """
    
    short_name = models.CharField(max_length=15)
    """
    Corresponds to usual HKN-name for positions (which is also usually the mailing list names)
    e.g. act, compserv, pres, vp, etc.
    """

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.short_name)

    def _get_permission_name(self):
        return "Members of %s" % self.name

    def _get_permission_codename(self):
        return "group_%s" % self.short_name
    
    def get_officer_title(self):
        if self.short_name in ("pres", "vp", "csec", "rsec", "treas"):
            return self.name
        return "%s Officer" % self.name

    def save(self, *args, **kwargs):
        if not self.id:
            position_type = ContentType.objects.get_for_model(Position)
            perm, created = Permission.objects.get_or_create(content_type = position_type, name = self._get_permission_name(), codename = self._get_permission_codename())
            if created:
                perm.save()
        
        super(Position, self).save(*args, **kwargs)
        if perm:
            self.permissions.add(perm)



class Person(User):
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

    For other objects for which models.ManyToManyField(Position) there are many-to-many correspondences (e.g. each Person has held lots of Positions, but
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

    imported = ImportedPeopleManager()

    realfirst = models.CharField(blank=True, max_length=30)
    """ 
    Real first name (the Person's official name, if it isn't already in L{first}).
    Can be empty if the Person's first name is their official name
    """
    

    school_email = models.EmailField(blank=True)
    """ 
    Person's official school email address. Probably a bad idea to issue lookup queries on this,
    see the object managers for some utility functions to help out with this 
    """

    positions = models.ManyToManyField(Position)
    """ A list of officership positions (i.e. not candidate committee) that this Person has held in the past. """


    member_type = models.IntegerField(db_column="member_type", choices = MEMBER_TYPE.choices())
    """ The person's member status. See L{hkn.info.constants.MEMBER_TYPE} for some more details. """

    def get_member_status(self):
        return MEMBER_TYPE._descriptions[self.member_type]
    member_status = property(get_member_status)

    def reconcile_status(self):
        officer_semesters = Officership.objects.filter(person=self).values_list('semester', flat=True)
        db_semester = nice_types.semester.SemesterField().get_db_prep_value(nice_types.semester.current_semester())
        if unicode(db_semester) in officer_semesters:
            self.member_type = MEMBER_TYPE.OFFICER
            self.is_staff = True
        elif self.member_type >= MEMBER_TYPE.OFFICER:
            self.member_type = MEMBER_TYPE.FOGIE
            self.is_staff = True
    
    
    def reconcile_groups(self):
        groups = Group.objects.filter(name__in = ("candidates", "members", "officers", "current_officers"))
        for g in self.groups.filter(id__in = groups.values('pk').query):
            self.groups.remove(g)
        groups_dict = {}
        for group in groups:
            groups_dict[group.name] = group

        if self.member_type == MEMBER_TYPE.CANDIDATE:
            self.groups.add(groups_dict["candidates"])
        if self.member_type >= MEMBER_TYPE.MEMBER:
            self.groups.add(groups_dict["members"])
        if self.member_type >= MEMBER_TYPE.EXOFFICER:
            self.groups.add(groups_dict["officers"])
        if self.member_type >= MEMBER_TYPE.OFFICER:
            self.groups.add(groups_dict["current_officers"])

    profile_picture = models.ForeignKey(Photo, null=True, related_name="persons")
    """ The person's profile picture"""

    def save_profile_picture(self, content, ext=".gif", save=True):
        uname = self.username
        self.profile_picture, created = Photo.objects.get_or_create(title="%s Profile Picture" % uname, is_public=False)
        self.profile_picture.image.save(self.generate_filename(uname + ext), content)
        if save:
            self.save()


    def generate_filename(self, original_filename):
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        new = "%s-%s" % (''.join([random.choice(digits) for i in xrange(15)]),
                         original_filename)
        return new
        
    

    officer_picture = models.ForeignKey(Photo, null=True, related_name="officers")
    """ The person's officer picture"""

    def save_officer_picture(self, content, ext=".gif", save=True):
        uname = self.username
        self.officer_picture, created = Photo.objects.get_or_create(title="%s Officer Picture" % uname, is_public=False)
        self.officer_picture.image.save(self.generate_filename(uname + ext), content)
        if save:
            self.save()

    def format_phone(self):
        """ Helper function for the above. """
        if len(self.phone) == 10:
            return "(" + self.phone[0:3] + ") " + self.phone[3:6] + "-" + self.phone[6:10]
        else:
            return self.phone

    phone = models.CharField(max_length=20)
    """ Phone number, usually cell phone. """

    phone_number = property(format_phone)

    privacy = PickleField()

    def __unicode__(self):
        return "%s %s %s (%s)" % (str(self.id), self.first_name, self.last_name, self.email )

    def get_current_position(self):
        officerships = self.officership_set.filter(semester = nice_types.semester.current_semester().abbr())
        if len(officerships) == 0:
            return None
        return officerships[0].position

    def get_committee(self):
        if self.member_type == MEMBER_TYPE.CANDIDATE:
            committee_name = self.candidateinfo.candidate_committee.name
            if committee_name and len(committee_name) > 0:
                return "%s Candidate" % (committee_name)
        elif self.member_type == MEMBER_TYPE.OFFICER and self.get_current_position():
                return self.get_current_position().get_officer_title()
        return ""
    
    def get_current_status(self):
        status = self.get_committee()
        if len(status) == 0:
            status = self.member_status
        return status

    def get_name(self):
        """
        Returns the person's full name (first + last).
        """
        return "%s %s" % (self.first_name, self.last_name)
    name = property(get_name)
    
    def get_abbr_name(self, dot=True):
        if dot:
            return "%s %s." % (self.first_name, self.last_name[0])
        else:
            return "%s %s" % (self.first_name, self.last_name[0])
    abbr_name = property(get_abbr_name)

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
            self.member_type = MEMBER_TYPE.MEMBER
        else:
            self.member_type = MEMBER_TYPE.CANDIDATE

    def save(self, *args, **kwargs):
        if type(self.privacy) != type({}):
            self.privacy = {}
        is_update = self.id is not None
        super(Person, self).save(*args, **kwargs)
        self.reconcile_groups()
        if not is_update:
            self.groups.add(Group.objects.get(name="everyone"))

    def get_picture_url(self, method="get_profilepic_url"):
        obj = self
        if hasattr(self, 'restricted'):
            obj = self.restricted
        if obj.officer_picture is not None:
            return getattr(obj.officer_picture, method)()
        if obj.profile_picture is not None:
            return getattr(obj.profile_picture, method)()
        return BlankImage().url


    class RestrictedPerson(object):
        def __init__(self, person, accessor):
            self.person = person
            self.privacy = person.privacy
            self.accessor_type = accessor.member_type
            self.view_all = accessor.has_perm("info.view_restricted")

        def blanktype(self, value):
            if type(value) == types.StringType:
                return ""
            elif isinstance(value, (models.fields.files.ImageFieldFile, Photo)):
                return self.BlankImage()
    
        def __getattr__(self, attr):
            if (self.accessor_type >= self.privacy.get(attr, -1)) or self.view_all:
                return getattr(self.person, attr)
            return self.blanktype(getattr(self.person, attr))

    def set_restricted_accessor(self, accessor):
        setattr(self,'restricted', Person.RestrictedPerson(self, accessor))

    class QuerySet(QuerySet):
        def from_email(self, email):
            email = normalize_email(email)
            return self.get(Q(school_email__iexact = email) | Q(email__iexact = email))
            
        def email_contains(self, email):
            email = normalize_email(email)
            return self.filter(Q(school_email__iexact = email) | Q(email__iexact = email))
    
        def filter_restricted(self, accessing_user):
            person_ctype = ContentType.objects.get_for_model(Person)
            self = self.exclude(member_type__lte = MEMBER_TYPE.REGISTERED)
            if not accessing_user.has_perm("info.view_excandidates"):
                self = self.exclude(member_type = MEMBER_TYPE.EXCANDIDATE)
            if not accessing_user.has_perm("info.view_candidates"):
                self = self.exclude(member_type = MEMBER_TYPE.CANDIDATE)
            if not accessing_user.has_perm("info.view_members"):
                self = self.exclude(Q(member_type = MEMBER_TYPE.MEMBER) | Q(member_type = MEMBER_TYPE.EXOFFICER))
            if not accessing_user.has_perm("info.view_officers"):
                self = self.exclude(member_type = MEMBER_TYPE.OFFICER)
            return self

        def ft_query(self, query):
            persons = self
            if query and len(query.strip()) != 0:
                for q in query.split(" "):
                    if len(q.strip()) == 0:
                        continue
                    persons = persons.filter(Q(first_name__icontains = q) | Q(last_name__icontains = q) | Q(username__icontains = q))
            return persons

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["first_name", "last_name"]
        permissions = (("view_officers", "View Officer Information"),
                       ("view_members", "View Member Information"),
                       ("view_candidates", "View Candidate Information"),
                       ("view_excandidates", "View Ex-Candidate Information"),
                       ("view_restricted", "View Restricted Information"))

from course.models import Course

class ExtendedInfo(models.Model):
    """
    ExtendedInfo for a Person, so that we don't have to store all of this information along with the main Person class.

    Due to incomplete records from semesters past, not all of this information may be present for many people, so be sure
    to sanity check!
    """

    person = models.OneToOneField(Person, primary_key = True)
    """A reference to a L{Person} object. To get a handle of the associated Person, do::
        >>>> candidateinfo.person"""
        
    sid = models.CharField(max_length=10)
    """ The person's SID. Try to use this as little as possible, will be phased out gradually. """

    grad_semester = semester.SemesterField(null=True)
    """ The person's graduation semester. Usually taken at initiation time, so subject to change. """

    grad_student = models.BooleanField()
    """ Is the person a grad student? """
    
    local_addr = models.TextField()
    """ Local address """

    perm_addr = models.TextField()
    """ Permanent (home) address """

    aim_sn = models.TextField()
    """ AIM Screen Name """

    current_courses = models.ManyToManyField(Course)

    def __unicode__(self):
        return "%s Extended" % (self.person.name)


class OfficershipManager(QuerySetManager):
    def for_current_semester(self, *args, **kwargs):
        return self.get_query_set().for_current_semester(*args, **kwargs)

class Officership(models.Model):
    """
    The official record of Officership in HKN. Brings together a L{Person}, L{Position}, and L{semester}.

    If Lahini Arunachalam was VP in fa07, then the corresponding officership object would have
    person = Lahini, position = vp, semester = fa07
    """
 
    objects = OfficershipManager()       

    officership_id = models.AutoField(primary_key = True)


    semester = nice_types.semester.SemesterField()
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

    def __unicode__(self):
        return "%s %s %s" % (self.person.name, self.semester, self.position.short_name)

    def save(self, *args, **kwargs):
        super(Officership, self).save(*args, **kwargs)
        self.person.reconcile_status()
        self.person.groups.add(self.position)
        self.person.save()

    class QuerySet(QuerySet):
        def for_current_semester(self):
            return self.filter(semester=semester.current_semester())

    class Meta:
        unique_together = ("person", "position", "semester")

from hkn.info import admin
