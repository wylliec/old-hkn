#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.models import *
from hkn.auth.models import *

hkn_positions = (("pres", "President"),
("vp", "Vice President"),
("rsec", "Recording Secretary"),
("csec", "Corresponding Secretary"),
("tres", "Treasurer"),
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

hkn_permissions = (
("everyone", "Everyone!"),
("officers", "Officers only!"),
("candidates", "Candidates!"),
("generic_permission", "Generic Permission"),
("another_permission", "Some other permission"),
)

for p in hkn_permissions:
	perm = Permission(codename = p[0], name = p[1])
	perm.save()

for hkn_pos in hkn_positions:
	if len(hkn_pos[0]) > 0:
		perm = Permission(codename = "group_" + hkn_pos[0], name = "Members of " + hkn_pos[1])
		perm.save()

		g = Group(name = hkn_pos[0])
		g.save()
		if perm is not None:
			g.permissions.add(perm)
		g.save()

	p = Position(short_name = hkn_pos[0], long_name = hkn_pos[1])
	p.save()


g = Group(name = "everyone")
g.save()
g = Group(name = "candidates")
g.save()
g = Group(name = "officers")
g.save()
g = Group(name = "members")
g.save()
