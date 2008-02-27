from django.db import models
from hkn.event.constants import EVENT_TYPE
from hkn.info.models import *
from hkn.event.models import *
import os


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




