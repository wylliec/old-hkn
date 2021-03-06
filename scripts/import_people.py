#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
import re, django, sys
import hkn_settings
from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import *
from hkn.cand.models import *
from django.contrib.auth.models import *
from hkn.info.utils import *
from photologue.models import *
from nice_types.semester import Semester


def import_people(filename, member_status):
    print "Importing from %s with member status %s" % (filename, MEMBER_TYPE[member_status])
    f = file(filename, 'r')
    for line in f:
        addLine(line, member_status)

lion_file_content = ContentFile(file('lion.gif', 'rb').read())

def make_username(first, last):
    uname = "imported__%s" % (str(first[0] + last)).lower()
    count = 0
    while True:
        try:
            Person.objects.get(username = uname)
            count += 1
            uname = uname + str(count)
        except Person.DoesNotExist:
            return uname
    

def addLine(line, member_status):
    line = line.replace('"', "")
    (first, last, realfirst, cand_com, email, lp, pp, la, pa, sid, gradsem, candsem) = line.split("\t")

    first = first.strip()
    last = last.strip()
    realfirst = realfirst.strip()

    email = normalize_email(email)
    try:
        p = Person.objects.from_email(email)
        print "Found duplicate person with email %s!" % email
        p.delete()
    except Person.DoesNotExist:
        pass

    uname = make_username(first, last)

    c = Person.objects.create_person(first, last, uname, email, member_status, password=None)

    if len(lp.strip()) > 0:
        c.phone = lp.strip()
    else:
        c.phone = pp.strip()
    if email.find("berkeley.edu") == -1:
        c.school_email = email

    c.realfirst = realfirst
    c.is_active = False
    c.save_profile_picture(lion_file_content)
    c.save()

    ci = ExtendedInfo()
    ci.local_addr = la.strip()
    ci.perm_addr = pa.strip()
    ci.sid = sid.strip()
    ci.grad_semester = None
    gradsem = gradsem.strip()
    if len(gradsem) > 0:
        ci.grad_semester = Semester(gradsem)
    ci.person = c
    ci.save()

    candidateinfo = CandidateInfo()
    candidateinfo.person = c
    candidateinfo.candidate_semester = candsem.strip()

    com = normalize_committee_name(cand_com)
    if com == "":
        print "Could not match committee: " + cand_com
    candidateinfo.candidate_committee = Position.objects.get(short_name = com)
    candidateinfo.comment = ""
    candidateinfo.initiated = False

    candidateinfo.save_candidate_picture(lion_file_content)
    candidateinfo.save()

everyoneGroup = Group.objects.get(name = "everyone")
candidatesGroup = Group.objects.get(name = "candidates")

if __name__ == "__main__":
    w = raw_input("Which data set to import? 'c' for candidates, anything else for other: ")
    if w.strip() == "c":
        import_people("data/info-candidates-sp08.tsv", MEMBER_TYPE.CANDIDATE)
    else:
        import_people("data/info-people.tsv", MEMBER_TYPE.EXCANDIDATE)
