#!/usr/bin/env python2.4
from django.core.management import setup_environ
import re, django, sys, pickle, glob

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.event.models import *


def import_officers(filename):
	f = file(filename, 'r')
	print "Importing from: " + filename
	
	officerships = pickle.load(f)

	for os in officerships:
		print os

		per = matchPerson(os[0])
		pos = matchPosition(os[1])
		
		o = Officership()
		o.semester = os[2]
		o.person = per
		o.position = pos
		o.save()

		g = Group.objects.get(name = pos.short_name)
		per.user.groups.add(g)
		per.member_status = Person.member_status_values['Current Officer']
		per.save()

def matchPerson(email):
	try:
		p = Person.objects.from_email(normalizeEmail(email))
		return p
	except Person.DoesNotExist:
		print "Error: email " + email + " not found! Pkl file invalid"
		pass
	return None


def matchPosition(name):
	try:
		p = Position.objects.get(short_name = name.strip())
		return p
	except ObjectDoesNotExist:
		print "Error: short name " + name + " not found! Pkl file incorrect"
		pass
	return None


officer_infos = glob.glob("data/officer-info-*.pkl")
for officer_info in officer_infos:
	import_officers(officer_info)
