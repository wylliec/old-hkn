#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
import hkn.semester

from hkn.info.constants import MEMBER_TYPE

officership_filename = "data/officership-all.pkl"

print "Importing cached officership records"
def import_officers():
    global officership_filename
    f = file(officership_filename, 'r')
    officership_by_semester = pickle.load(f)

    for officership_semester in officership_by_semester.values():
        for officership in officership_semester:
            person = matchPerson(officership[0])
            username = officership[1]
            position = matchPosition(officership[2])
            semester = officership[3]

            if person is None:
                print "could not match %s" % officership[0]
                continue
            if position is None:
                print "could not match %s" % officership[2]
                continue
            
    

            os, created = Officership.objects.get_or_create(person = person, position = position, semester = semester)
            if not created:
                print "Officership: " + str(os) + " already existed!"



def matchPerson(email):
    try:
        p = Person.objects.from_email(normalizeEmail(email))
        return p
    except ObjectDoesNotExist:
        pass


def matchPosition(name):
    try:
        p = Position.objects.get(short_name = name.strip())
        return p
    except ObjectDoesNotExist:
        pass

    try:
        p = Position.objects.get(name = name.strip())
        return p
    except ObjectDoesNotExist:
        pass

    return None

if __name__ == "__main__":
    import_officers()

