#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.utils import *

pklFilename = "data/officer_uname.pkl"
pklFile = file(pklFilename, 'r')
    


def matchPerson(email):
    try:
        p = Person.objects.from_email(normalizeEmail(email))
        return p
    except Person.DoesNotExist:
        print "Error: email " + email + " not found! Pkl file invalid"
    return None

oss = pickle.load(pklFile)
for os in oss:
    person = matchPerson(os[0])
    u = person.user
    print "Setting %s's username to %s" % (person.name(), os[1])
    u.username = os[1]
    u.save()

