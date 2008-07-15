from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import *
from django.core import urlresolvers

from hkn.info.models import *
from hkn import semester
from hkn.info.constants import MEMBER_TYPE
from hkn.gcal import gcalInterface
import os, pickle
from constants import RSVP_TYPE, EVENT_TYPE
from string import atoi

from nice_types.db import PickleField, QuerySetManager

import request
import request.utils

try:
    from hkn.hknsettings import GCAL_ENABLED
except:
    GCAL_ENABLED = False


class AllEventsManager(QuerySetManager):
    def query(self, query, events = None):
        if events == None:
            events = self.get_query_set()
        if query and len(query.strip()) != 0:
            for q in query.split(" "):
                if len(q.strip()) == 0:
                    continue
                events = events.filter(Q(name__icontains = q) | Q(location__icontains = q) | Q(description__icontains = q))
        return events

class FutureEventsManager(AllEventsManager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(FutureEventsManager, self).get_query_set().filter(start_time__gte = start_time)

class PastEventsManager(AllEventsManager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(PastEventsManager, self).get_query_set().filter(start_time__lt = start_time)

class TodayEventsManager(AllEventsManager):
        def get_query_set(self):
                start_time = datetime.date.today() 
                return super(TodayEventsManager, self).get_query_set().filter(start_time__year = start_time.year, start_time__month = start_time.month, start_time__day = start_time.day)

class SemesterEventsManager(AllEventsManager):
    def get_query_set(self):
        start_time = semester.getSemesterStart()
        return super(SemesterEventsManager, self).get_query_set().filter(start_time__gte = start_time)


class Event(models.Model):
    objects = AllEventsManager()
    future = FutureEventsManager()
    past = PastEventsManager()
    semester = SemesterEventsManager()
    today = TodayEventsManager()

    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    rsvp_type = models.IntegerField(choices = RSVP_TYPE.choices())

    rsvp_block_size = models.IntegerField()

    rsvp_transportation_necessary = models.BooleanField()
    

    view_permission = models.ForeignKey(Permission, related_name = 'event_view_required')
    rsvp_permission = models.ForeignKey(Permission, related_name = 'event_rsvp_required')

    


    event_type = models.CharField(max_length = 10, choices = EVENT_TYPE.choices())

    gcal_id = models.TextField(blank = True)

    def __unicode__(self):
        return self.name

    class QuerySet(QuerySet):
        def filter_permissions(self, user):
            perms = user.get_all_permissions()
            events = list(self)
            for event in events:
                view_perm_code = "%s.%s" % (event.view_permission.content_type.app_label, event.view_permission.codename)
                if view_perm_code not in perms:
                    events.remove(event)
            return events

    def rsvp_whole(self):
        return self.rsvp_type == RSVP_TYPE.WHOLE

    def rsvp_none(self):
        return self.rsvp_type == RSVP_TYPE.NONE

    def rsvp_block(self):
        return self.rsvp_type == RSVP_TYPE.BLOCK

    def get_event_type(self):
        return EVENT_TYPE[self.event_type]

    def get_rsvp_type(self):
        return RSVP_TYPE[self.rsvp_type]

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
        if gcal and GCAL_ENABLED:
            gcalInterface.eventSaved(self)
        models.Model.save(self)

    def delete(self, gcal = True):
        if gcal and GCAL_ENABLED:
            gcalInterface.eventDeleted(self)
        models.Model.delete(self)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"


def getCandidates():
    return Person.candidates.all()
    #return Person.fogies.all()

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
    

    def order(self, sort_field, rsvps):
        # the below should no longder be necessary with queryset-refactor
        # but let's keep it around for now just in case...
        return rsvps.order_by(sort_field)
        if sort_field.find("event__") != -1:
            sort_field = sort_field.replace("event__", "")
            return RSVP.objects.order_by_event_field(sort_field, rsvps)
        if sort_field.find("person__") != -1:
            sort_field = sort_field.replace("person__", "")
            return RSVP.objects.order_by_person_field(sort_field, rsvps)
        return rsvps.order_by(sort_field)
    

    def order_by_event_field(self, event_field, objects):
        negate = ""
        if event_field[0] == "-":
            event_field = event_field[1:]
            negate = "-"
        return objects.extra(where=["event_rsvp.event_id = event_event.id"], tables=["event_event"]).order_by(negate + "event_event." + event_field)
    

    def order_by_person_field(self, person_field, objects):
        negate = ""
        if person_field[0] == "-":
            person_field = person_field[1:]
            negate = "-"		
        return objects.extra(where=["event_rsvp.person_id = info_person.id"], tables=["info_person"]).order_by(negate + "info_person." + person_field)

    def query_event(self, query, rsvps = None):
        if rsvps == None:
            rsvps = self.get_query_set()
            

        if query and len(query.strip()) != 0:
            for q in query.split(" "):
                if len(q.strip()) == 0:
                    continue
                rsvps = rsvps.filter(Q(event__name__icontains = q) | Q(event__location__icontains = q) | Q(event__description__icontains = q))
        return rsvps
    

    def query_person(self, query, rsvps = None):
        if rsvps == None:
            rsvps = self.get_query_set()
            

        if query and len(query.strip()) != 0:
            for q in query.split(" "):
                if len(q.strip()) == 0:
                    continue
                rsvps = rsvps.filter(Q(person__first__icontains = q) | Q(person__last__icontains = q) | Q(person__username__icontains = q))
        return rsvps
    

    def query(self, query, rsvps = None):
        if rsvps == None:
            rsvps = self.get_query_set()
            

        if query and len(query.strip()) != 0:
            for q in query.split(" "):
                if len(q.strip()) == 0:
                    continue
                rsvps = rsvps.filter(Q(event__name__icontains = q) | Q(event__location__icontains = q) | Q(event__description__icontains = q)
                                     | Q(person__first__icontains = q) | Q(person__last__icontains = q) | Q(person__username__icontains = q))
        return rsvps

        

class FutureRSVPManager(RSVPManager):
        def get_query_set(self):
                start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(FutureRSVPManager, self).get_query_set().filter(event__start_time__gte = start_time)


class RSVP(models.Model):
    objects = RSVPManager()
    future = FutureRSVPManager()

    id = models.AutoField(primary_key = True)
    event = models.ForeignKey(Event)
    person = models.ForeignKey(Person)

    transport = models.IntegerField()

    comment = models.TextField(blank = True)

    vp_confirm = models.NullBooleanField(default = None)
    vp_comment = models.TextField(blank = True)

    # store pickle'd data that is relevant
    rsvp_data = PickleField()

    def is_block(self):
        return self.event.rsvp_type == RSVP_TYPE.BLOCK

    def get_block_descriptions(self):
        desc = []
        for block in self.rsvp_data.blocks:
            bn = atoi(block)
            desc.append(self.event.get_formatted_time_range_for_block(bn))
        return ", ".join(desc)

    def __str__(self):
        e = self.event
        return str(self.person) + " : " + str(self.event)

    def request_confirmation(self):
        return request.utils.request_confirmation(self, self.person, Permission.objects.get(codename="group_vp"))

    class Meta:
        unique_together = (("event", "person"),)

def get_rsvp_metainfo(rsvp, request):
    metainfo = {}

    metainfo['title'] = "Confirm RSVP"
    metainfo['description'] = "Confirm %s's RSVP for %s" % (rsvp.person.name, rsvp.event.name)
    metainfo['links'] = (("rsvp", urlresolvers.reverse("hkn.event.rsvp.rsvp.view", kwargs = {"rsvp_id" : rsvp.id})),
                     ("person", urlresolvers.reverse("hkn.info.person.view", kwargs = {"person_id" : rsvp.person_id})),
                     ("event", urlresolvers.reverse("hkn.event.event.view", kwargs = {"event_id" : rsvp.event_id})))
    metainfo['confirmed'] = rsvp.vp_confirm 
    return metainfo

request.register(RSVP, get_rsvp_metainfo, confirmation_attr='vp_confirm')


class RSVPData:
    def __init__(self, blocks=()):
        self.blocks = tuple(blocks)

    def __str__(self):
        return "Blocks: " + str(self.blocks)

from hkn.event import admin
