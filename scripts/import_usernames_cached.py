#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
import re, django, sys, pickle, os

import hkn_settings

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
        path = os.path.join(os.path.expanduser('~/hkn-website-images/officerpics/'), "%s." % offs[1])
        if os.path.exists(path + ext):
            picfile = SimpleUploadedFile("%s.%s" % (offs[1], ext), file(path+ext).read())
            person.save_officer_picture_file(picfile.file_name, picfile)
    person.save()

