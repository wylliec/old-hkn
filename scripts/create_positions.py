#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.models import *
from django.contrib.auth.models import *

hkn_positions = (("pres", "President"),
("vp", "Vice President"),
("rsec", "Recording Secretary"),
("csec", "Corresponding Secretary"),
("treas", "Treasurer"),
("deprel", "Department Relations"),
("studrel", "Student Relations"),
("alumrel", "Alumni Relations"),
("pub", "Publicity"),
("examfiles", "Exam Files"),
("indrel", "Industrial Relations"),
("bridge", "Bridge"),
("act", "Activities"),
("compserv", "Computing Services"),
("ejc", "EJC Representative"),
("tutor", "Tutoring"),
("alumadvisor", "Alumni Advisor"),
("facadvisor", "Faculty Advisor"),
("", "Unknown"))

def main():
    print "Creating Positions for HKN committees"
    for hkn_pos in hkn_positions:
        p = Position(short_name = hkn_pos[0], name = hkn_pos[1])
        p.save()
