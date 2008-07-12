#!/usr/bin/env python
import hkn_settings, pickle
from hkn.tutor.models import *
from hkn.info.models import *
from course.models import *

season = Season.objects.get(name="spring")
existed = 0
avail = pickle.load(file('data/tutor_data_avail_sp08.pkl'))
for av in avail:
    username, slot, office, preference = av
    person = Person.objects.get(username=username)
    ava, created = Availability.objects.get_or_create(person=person, slot=slot, office=office, season=season, year=2008, preference=preference)
    if not created:
        existed += 1

if existed > 0:
    print "%d availabilities already existed" % existed

existed = 0
assign = pickle.load(file('data/tutor_data_assign_sp08.pkl'))
for a in assign:
    username, slot, office, version = a
    person = Person.objects.get(username=username)
    ass, created = Assignment.objects.get_or_create(person=person, slot=slot, office=office, season=season, year=2008, version=version)
    if not created:
        existed += 1

if existed > 0:
    print "%d assignments already existed" % existed

existed = 0
cantutors = pickle.load(file('data/tutor_data_cantutor_sp08.pkl'))
for a in cantutors:
    username, cname, current = a
    person = Person.objects.get(username=username)
    course = Course.objects.query(cname)[0]
    cantut, created = CanTutor.objects.get_or_create(person=person, course=course, season=season, year=2008, current=current)
    if not created:
        existed += 1

if existed > 0:
    print "%d CanTutors already existed" % existed


