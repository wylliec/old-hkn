#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
import re, django, sys, pickle, os

import hkn_settings
from hkn.settings import IMAGES_PATH

from hkn.info.models import *
from hkn.info.utils import *

pklFilename = "data/officer_uname.pkl"
pklFile = file(pklFilename, 'r')
    

def matchPerson(email):
    try:
        p = Person.objects.from_email(normalize_email(email))
        return p
    except Person.DoesNotExist:
        print "Error: email " + email + " not found! Pkl file invalid"
    return None

def main():
    oss = pickle.load(pklFile)
    print "Setting HKN Officer usernames"
    for offs in oss:
        person = matchPerson(offs[0])
        person.username = offs[1]
        for ext in ("gif", "jpg"):
            name = "%s.%s" % (offs[1], ext)
            path = os.path.join(os.path.join(IMAGES_PATH, 'officerpics/'), name)
            if os.path.exists(path):
                picfile = ContentFile(file(path).read())
                person.officer_picture.save(person.generate_filename(name), picfile)
        person.save()

if __name__ == "__main__":
    main()

