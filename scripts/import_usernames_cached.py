#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
import re, django, sys, pickle, os

import hkn_settings
from hkn.settings import IMAGES_PATH

from hkn.info.models import *
from hkn.info.utils import *

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
print "Setting HKN Officer usernames"
for offs in oss:
    person = matchPerson(offs[0])
    person.username = offs[1]
    for ext in ("gif", "jpg"):
        name = "%s.%s" % (offs[1], ext)
        path = os.path.join(os.path.join(IMAGES_PATH, 'officerpics/'), name)
        if os.path.exists(path):
            picfile = SimpleUploadedFile(name, file(path).read())
            person.save_officer_picture_file(picfile.name, picfile)
    person.save()

