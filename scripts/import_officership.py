#!/usr/bin/env python2.4
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.utils import *
from hkn.info.constants import MEMBER_TYPE
from hkn import semester


def import_officers(filename):
	f = file(filename, 'r')
	semester = filename.replace("officer-info-", "").replace(".txt", "")
	pklFilename = filename.replace(".txt", ".pkl")
	
	p = re.compile("(?P<name>.*)\((?P<user>.*)\)\n(?P<email>.*)\n")
	matches = p.findall(f.read())
	officers = []
	for match in matches:
		officer = matchPerson(match[0].strip(), match[1], match[2])
		if officer is None:
			print "Could not match: " + str(match)
			continue
		print "Matched: " + str(match)
		officers.append(officer)
	print officers
	officership = []
	for officer in officers:
		position = None
		while position is None:
			position_name = raw_input("What position was %s in %s? " % (officer.name(), semester))
			position = matchPosition(position_name)
			if position is None:
				print "Could not match position! try again"
		o = Officership()
		o.semester = semester
		o.person = officer
		o.position = position
		o.save()
		g = Group.objects.get(name = position.short_name)
		officer.user.groups.add(g)
		if semester == semester.getCurrentSemester():
			officer.member_status = MEMBER_TYPE.OFFICER
		else:
			officer.member_status = MEMBER_TYPE.EXOFFICER
		officer.save()
		officership.append((officer.email(), position.short_name, semester))
	pklFile = file(pklFilename, 'w')
	pickle.dump(officership, pklFile)
	print officership


def matchPerson(name, username, email):
	try:
		p = Person.objects.from_email(normalizeEmail(email))
		return p
	except ObjectDoesNotExist:
		pass

	t = name.strip().split(" ")
	try:
		p = Person.objects.get(first = t[0], last = t[len(t)-1])
		return p
	except ObjectDoesNotExist:
		pass
	return None

def matchPosition(name):
	try:
		p = Position.objects.get(short_name = name.strip())
		return p
	except ObjectDoesNotExist:
		pass

	try:
		p = Position.objects.get(long_name = name.strip())
		return p
	except ObjectDoesNotExist:
		pass

	return None

officer_infos = glob.glob("data/officer-info-*.txt")
for officer_info in officer_infos:
	import_officers(officer_info)
