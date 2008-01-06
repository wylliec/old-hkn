#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.utils import *

for o in Person.all_officers.all():
    u = o.user
    uname = raw_input("What is %s's username? [%s] " % (o.name(), u.username))
    if len(uname.strip()) != 0:
        u.username = uname
        u.save()

oss = []
for o in Person.all_officers.all():
    os = (o.email(), o.user.username)
    oss.append(os)

print oss

pklFilename = "data/officer_uname.pkl"
pklFile = file(pklFilename, 'w')
pickle.dump(tuple(oss), pklFile)

