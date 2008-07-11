from django.db import models
from hkn.event.constants import EVENT_TYPE
from hkn.info.models import *
from hkn.event.models import *
import os

import request
import request.utils
from request.models import Request

class CandidateApplication(models.Model):
    person = models.ForeignKey(Person)

    transfer = models.BooleanField()
    current_year = models.CharField(max_length = 2)
    eecs_option = models.IntegerField()
    committee_choices = models.CharField(max_length = 15)

    q1 = models.TextField()
    q2 = models.TextField()
    q3 = models.TextField()
    q4 = models.TextField()
    q5 = models.TextField()

class Challenge(models.Model):
    candidate = models.ForeignKey(Person)

    title = models.CharField(max_length=40)
    description = models.TextField()
    
    confirmed = models.BooleanField()

    confirm_request = models.ForeignKey(Request)

    def request_confirmation(self, confirm_with):
        self.confirm_request =  request.utils.request_confirmation(self, self.candidate.user, permission=None, permission_user=confirm_with)
        self.save()
        return self.confirm_request

    def save(self):
        if self.confirm_request is None:
            raise Exception('Challenge must request confirmation first! call request_confirmation to save')
        super(Challenge, self).save()

def get_challenge_metainfo(challenge, request):
    metainfo = {}
    metainfo['title'] = 'Confirm Challenge'
    metainfo['description'] = '''Confirm %s's challenge "%s" ''' % (challenge.candidate.name(), challenge.title)
    metainfo['links'] = tuple()
    metainfo['confirmed'] = challenge.confirmed

request.register(Challenge, get_challenge_metainfo, confirmation_attr='confirmed')

