#!/usr/bin/env python
import hkn_settings, pickle
from hkn.tutor.models import *
from hkn.info.models import *
from course.models import *

season = Season.objects.get(name="spring")

avail = pickle.load(file('data/tutor_data_sp08.pkl'))
for av in avail:
    username, slot, office, preference = av
    person = Person.objects.get(username=username)
    ava, created = Availability.objects.get_or_create(person=person, slot=slot, office=office, season=season, year=2008, preference=preference)
    if not created:
        print "Availability already existed!"


