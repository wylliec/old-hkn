from django.db import models
from django.db import connection
from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.core import urlresolvers
from django.template.defaultfilters import slugify
from django.db.models import Q

from hkn.event.constants import EVENT_TYPE
from hkn.event.rsvp.constants import RSVP_TYPE
from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import Person

from string import atoi
import os, pickle
import datetime

from nice_types.db import PickleField, QuerySetManager
from nice_types import semester
import request.utils

class AllEventsManager(QuerySetManager):
    def ft_query(self, query):
        return self.get_query_set().ft_query(query)
        
    def filter_permissions(self, user):
        return self.get_query_set().filter_permissions(user)
    
    def annotate_rsvp_count(self, *args, **kwargs):
        return self.get_query_set().annotate_rsvp_count(*args, **kwargs)

class PublicEventsManager(AllEventsManager):
        def get_query_set(self):
                return super(PublicEventsManager, self).get_query_set().filter(view_permission__codename = "hkn_everyone")

class FutureEventsManager(AllEventsManager):
        def get_query_set(self):
                #start_time = datetime.date.today() - datetime.timedelta(days = 1)
                return super(FutureEventsManager, self).get_query_set().filter(start_time__gte = datetime.date.today())

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
        start_time = semester.current_semester().start_date
        return super(SemesterEventsManager, self).get_query_set().filter(start_time__gte = start_time)


class Event(models.Model):
    objects = AllEventsManager()
    public = PublicEventsManager()
    future = FutureEventsManager()
    past = PastEventsManager()
    semester = SemesterEventsManager()
    today = TodayEventsManager()

    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, max_length=125)
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

    def generate_unique_slug(self):
        base = slugify("%s-%s" % (self.start_time.strftime("%m-%d-%y"), self.name))
        for i in range(100):
            slug = base
            if i>0:
                slug = "%s-%d" % (base, i)
            query = Event.objects.filter(slug=slug).exclude(pk=self.id)
            if query.count() == 0:
                return slug
        raise Exception("Exhausted 100 slug values!")
            

    class QuerySet(QuerySet):
        def ft_query(self, query):
            if query and len(query.strip()) != 0:
                for q in query.split(" "):
                    if len(q.strip()) == 0:
                        continue
                    self = self.filter(Q(name__icontains = q) | Q(location__icontains = q) | Q(description__icontains = q))
            return self    
    
        def _filter_permissions(self, permissions):
            sql = """
                SELECT e.id
                FROM auth_permission p INNER JOIN event_event e ON (e.view_permission_id = p.id)
                WHERE p.codename IN ('%s')
            """ % "','".join(permissions)

            cursor = connection.cursor()
            cursor.execute(sql)
            f = cursor.fetchall()
            ids = set([a[0] for a in f])
            return ids
    
        def filter_permissions(self, user):
            perms = user.get_all_permissions()
            perms = map(lambda p: str(p.split(".")[1]), perms)
            ids = self._filter_permissions(perms)
            return self.filter(id__in=ids)
        
        def annotate_rsvp_count(self):
            return self.extra(
                              select = {
                                        'rsvp_count': 'SELECT COUNT(*) FROM event_rsvp WHERE event_rsvp.event_id = event_event.id'
                                        }
                              )

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

    def save(self, force_update_slug=False, *args, **kwargs):
        if not self.slug or self.slug == "slug" or force_update_slug:
            self.slug = self.generate_unique_slug()
        super(Event, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

class RSVPManager(models.Manager):
    def get_confirmed_for_event(self, e):
        return self.get_query_set().filter(event = e, vp_confirm = True)

    def get_confirmables_for_event(self, e):
        return e.rsvp_set.filter(person__in = Person.candidates.all())

    def get_attended_events(self, person):
        if person.member_status == MEMBER_TYPE.CANDIDATE:
            return self.get_query_set().filter(person = person, vp_confirm = True)
        return self.get_query_set().filter(person = person)

    def get_confirmed_events(self, person):
        return self.get_query_set().filter(person = person, vp_confirm = True)

    def query_event(self, query):
        return self.get_query_set().ft_query_event(query)
    

    def query_person(self, query):
        return self.get_query_set().ft_query_person(query)
    
    def query(self, query, rsvps = None):
        return self.get_query_set().ft_query(query)

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
        return self.event.rsvp_block()

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
    
    class QuerySet(QuerySet):
        def ft_query_event(self, query):    
            if query and len(query.strip()) != 0:
                for q in query.split(" "):
                    if len(q.strip()) == 0:
                        continue
                    rsvps = rsvps.filter(Q(event__name__icontains = q) | Q(event__location__icontains = q) | Q(event__description__icontains = q))
            return rsvps
        
    
        def ft_query_person(self, query):
            if query and len(query.strip()) != 0:
                for q in query.split(" "):
                    if len(q.strip()) == 0:
                        continue
                    rsvps = rsvps.filter(Q(person__first__icontains = q) | Q(person__last__icontains = q) | Q(person__username__icontains = q))
            return rsvps
        
    
        def ft_query(self, query):
            if query and len(query.strip()) != 0:
                for q in query.split(" "):
                    if len(q.strip()) == 0:
                        continue
                    rsvps = rsvps.filter(Q(event__name__icontains = q) | Q(event__location__icontains = q) | Q(event__description__icontains = q)
                                         | Q(person__first__icontains = q) | Q(person__last__icontains = q) | Q(person__username__icontains = q))
            return rsvps

    class Meta:
        unique_together = (("event", "person"),)

class RSVPData:
    def __init__(self, blocks=()):
        self.blocks = tuple(blocks)

    def __str__(self):
        return "Blocks: " + str(self.blocks)

from hkn.event import admin
from hkn.event import requests
