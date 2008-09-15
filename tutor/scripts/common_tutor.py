#!/usr/bin/env python
import setup_settings
from hkn.tutor.models import *
from hkn.info.models import *
from course.models import Course
import pickle

def avail_deserialize(a):
    return Availability(person=Person.objects.get(username=a[0]), slot=a[1], office=a[2], semester=a[3], preference=a[4]).save()

def avail_serialize(a):
    return (a.person.username, a.slot, a.office, a.semester.abbr(), a.preference)

def assign_deserialize(a):
    return Assignment(person=Person.objects.get(username=a[0]), slot=a[1], office=a[2], semester=a[3], version=a[4]).save()

def assign_serialize(a):
    return (a.person.username, a.slot, a.office, a.semester.abbr(), a.version)

def cantutor_deserialize(a):
    return CanTutor(person=Person.objects.get(username=a[0]), course=Course.objects.ft_query(a[1])[0], semester=a[2], current=a[3]).save()

def cantutor_serialize(c):
    return (c.person.username, c.course.short_name(space=True), c.semester.abbr(), c.current)

def load_clazz(clazz, d, s):
    f = file("data/%s.pkl" % clazz.__name__.lower())
    obs = pickle.load(f)
    [d(a) for a in obs]

def dump_clazz(clazz, d, s):
    f = file("data/%s.pkl" % clazz.__name__.lower(), "w")
    tp = map(s, clazz.objects.all())
    pickle.dump(tp, f)
    
towork = [
(Availability, avail_deserialize, avail_serialize),
(Assignment, assign_deserialize, assign_serialize),
(CanTutor, cantutor_deserialize, cantutor_serialize),
]

def main(load=False):
    for w in towork:
        if load:
            load_clazz(*w)
        else:
            dump_clazz(*w)
