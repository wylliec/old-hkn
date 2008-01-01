from django.db import models
from hkn.info.models import *
from hkn.auth.models import *
from hkn import semester
from hkn.info.constants import MEMBER_TYPE
from hkn.gcal import gcalInterface
import os, pickle
from constants import RSVP_TYPE, EVENT_TYPE
from string import atoi


class AllEventsManager(models.Manager):
	pass

class FutureEventsManager(models.Manager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(FutureEventsManager, self).get_query_set().filter(start_time__gte = start_time)

class PastEventsManager(models.Manager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(PastEventsManager, self).get_query_set().filter(start_time__lt = start_time)

class TodayEventsManager(models.Manager):
        def get_query_set(self):
                start_time = datetime.date.today() 
                return super(TodayEventsManager, self).get_query_set().filter(start_time__year = start_time.year, start_time__month = start_time.month, start_time__day = start_time.day)

class SemesterEventsManager(models.Manager):
	def get_query_set(self):
		start_time = semester.getSemesterStart()
		return super(SemesterEventsManager, self).get_query_set().filter(start_time__gte = start_time)


class Event(models.Model):
	objects = AllEventsManager()
	future = FutureEventsManager()
	past = PastEventsManager()
	semester = SemesterEventsManager()
	today = TodayEventsManager()

	event_id = models.AutoField(primary_key = True)
	name = models.CharField(maxlength=100)
	location = models.CharField(maxlength=100)
	description = models.TextField()
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()

	rsvp_type = models.IntegerField(choices = RSVP_TYPE.CHOICES)

	rsvp_block_size = models.IntegerField()

	rsvp_transportation_necessary = models.BooleanField()
	
	view_permission = models.ForeignKey(Permission, related_name = 'event_view_required')
	rsvp_permission = models.ForeignKey(Permission, related_name = 'event_rsvp_required')

	

	event_type = models.CharField(maxlength = 10, choices = EVENT_TYPE.CHOICES)

	gcal_id = models.TextField(blank = True)

	def __str__(self):
		return self.name

	def rsvp_whole(self):
		return self.rsvp_type == RSVP_TYPE.WHOLE

	def rsvp_none(self):
		return self.rsvp_type == RSVP_TYPE.NONE

	def rsvp_block(self):
		return self.rsvp_type == RSVP_TYPE.BLOCK

	def get_event_type(self):
		return EVENT_TYPE.CHOICES_DICT[self.event_type]

	def get_rsvp_type(self):
		return RSVP_TYPE.CHOICES_DICT[self.rsvp_type]

	def get_num_rsvp_blocks(self):
		if self.rsvp_type != RSVP_TYPE.BLOCK:
			return None
		td = (self.end_time - self.start_time)
		minutes = td.days * 60 * 24 + td.seconds / 60 + td.microseconds / 60000
		return minutes / self.rsvp_block_size

	def get_time_range_for_block(self, block_num):
		if self.rsvp_type != RSVP_TYPE.BLOCK:
			return None
		start_min = block_num * self.rsvp_block_size
		start_range = self.start_time + datetime.timedelta(minutes = start_min)
		end_range = start_range + datetime.timedelta(minutes = self.rsvp_block_size)
		return (start_range, end_range)

	def get_formatted_time_range_for_block(self, block_num, format = "%I:%M%p"):
		if self.rsvp_type != RSVP_TYPE.BLOCK:
			return None
		tr = self.get_time_range_for_block(block_num)
		return "%s - %s" % (tr[0].strftime(format), tr[1].strftime(format))

	def save(self, gcal = True):
		if gcal:
			gcalInterface.eventSaved(self)
		models.Model.save(self)

	def delete(self, gcal = True):
		if gcal:
			gcalInterface.eventDeleted(self)
		models.Model.delete(self)

def getCandidates():
	#return Person.candidates.all()
	return Person.fogies.all()

class RSVPManager(models.Manager):
	def getConfirmedForEvent(self, e):
		return self.get_query_set().filter(event = e, vp_confirm = True)

	def getConfirmablesForEvent(self, e):
		return e.rsvp_set.filter(person__in = getCandidates())

	def getAttendedEvents(self, person):
		if person.member_status == MEMBER_TYPE.CANDIDATE:
			return self.get_query_set().filter(person = person, vp_confirm = True)
		return self.get_query_set().filter(person = person)

	def getConfirmedEvents(self, person):
		return self.get_query_set().filter(person = person, vp_confirm = True)

	def get_query_set(self):
		return super(RSVPManager, self).get_query_set()

		
class FutureRSVPManager(RSVPManager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(FutureRSVPManager, self).get_query_set().filter(event__start_time__gte = start_time)


class RSVP(models.Model):
	objects = RSVPManager()
	future = FutureRSVPManager()

	rsvp_id = models.AutoField(primary_key = True)
	event = models.ForeignKey(Event)
	person = models.ForeignKey(Person)

	transport = models.IntegerField()

	comment = models.TextField(blank = True)

	vp_confirm = models.BooleanField()
	vp_comment = models.TextField(blank = True)

	# store pickle'd data that is relevant
	rsvp_data_pkl = models.TextField()

	def save(self):
		if self.vp_confirm == "":
			self.vp_confirm = False
		models.Model.save(self)

	def set_rsvp_data(self, rsvp_data):
		self.rsvp_data_pkl = pickle.dumps(rsvp_data)

	def get_rsvp_data(self):
		return pickle.loads(self.rsvp_data_pkl)

	def is_block(self):
		return self.event.rsvp_type == RSVP_TYPE.BLOCK


	def get_block_descriptions(self):
		rsvp_data = self.get_rsvp_data()
		desc = []
		for block in rsvp_data.blocks:
			bn = atoi(block)
			desc.append(self.event.get_formatted_time_range_for_block(bn))
		return ", ".join(desc)

	def __str__(self):
		e = self.event
		return str(self.person) + " : " + str(self.event)
			



class RSVPData:
	def __init__(self, blocks=()):
		self.blocks = tuple(blocks)

	def __str__(self):
		return "Blocks: " + str(self.blocks)



