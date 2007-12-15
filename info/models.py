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
		return super(MemberManager, self).get_query_set().filter(member_status = MEMBER_TYPE.MEMBER)

class PositionManager(models.Manager):
	def getPosition(self, com_name):
	        com_name = normalizeCommitteeName(com_name)
		return super(PositionManager, self).get_query_set().get(short_name = com_name)

class Position(models.Model):
	objects = PositionManager()
	position_id = models.AutoField(primary_key = True)
	short_name = models.CharField(maxlength=15)
	long_name = models.CharField(maxlength=50)

	def __str__(self):
		return "%s (%s)" % (self.long_name, self.short_name)


# Create your models here.
class Person(models.Model):
	people = objects = PeopleManager()
	candidates = CandidateManager()
	officers = OfficerManager()
	all_officers = AllOfficerManager()
	members = MemberManager()

	person_id = models.AutoField(primary_key = True)
	first = models.CharField(maxlength = 30)
	last = models.CharField(maxlength=30)
	realfirst = models.CharField(maxlength=30)
	school_email = models.CharField(maxlength=60)
	preferred_email = models.CharField(maxlength=60)
	positions = models.ManyToManyField(Position)


	member_status = models.IntegerField()

	def __str__(self):
		return "%s %s %s (%s)" % (str(self.person_id), self.first, self.last, self.email() )

	def email(self):
		if len(self.preferred_email) > 0:
			return self.preferred_email
		return self.school_email

	def name(self):
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
		

	

	def detail_url(self):
		return "/info/details/" + str(self.person_id)

	def is_initiated(self):
		return self.member_status >= MEMBER_TYPE.MEMBER

	def initiate(self, initiate = True):
		if initiate:
			self.member_status = MEMBER_TYPE.MEMBER
		else:
			self.member_status = MEMBER_TYPE.CANDIDATE

	class Admin:
		pass

class ExtendedInfo(models.Model):
	person = models.OneToOneField(Person, primary_key = True)
	sid = models.CharField(maxlength=10)
	grad_semester = models.CharField(maxlength=5)
	local_phone = models.CharField(maxlength=20)
	perm_phone = models.CharField(maxlength=20)
	local_addr = models.CharField(maxlength=100)
	perm_addr = models.CharField(maxlength=100)

	def __str__(self):
		return "%s %s %s (%s)" % (self.person.first, self.person.last, self.sid, self.get_phone() )

	def get_phone(self):
		if self.local_phone is not None and len(self.local_phone) > 0:
			return self.format_phone(self.local_phone)
		return self.format_phone(self.perm_phone)
	
	def format_phone(self, phone):
		if len(phone) == 10:
			return "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]
		else:
			return phone

	class Admin:
		pass

class CandidateInfo(models.Model):
	person = models.OneToOneField(Person, primary_key = True)
	candidate_semester = models.CharField(maxlength=5)
	candidate_committee = models.ForeignKey(Position)
	initiation_comment = models.TextField()

	def __str__(self):
		return "%s %s (%s)" % (self.candidate_committee.short_name, self.candidate_semester, self.initiation_comment)
			


class Officership(models.Model):
	officership_id = models.AutoField(primary_key = True)
	semester = models.CharField(maxlength=5)
	position = models.ForeignKey(Position)
	person = models.ForeignKey(Person)

	def __str__(self):
		return "%s %s %s %s" % (self.semester, self.position.short_name, self.person.first, self.person.last)
