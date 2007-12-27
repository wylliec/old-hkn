#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys, pickle

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.utils import *
import hkn.semester

from hkn.info.constants import MEMBER_TYPE

officership_filename = "data/officership-all.pkl"

def import_officers():
	global officership_filename
	f = file(officership_filename, 'r')
	officership_by_semester = pickle.load(f)

	for officership_semester in officership_by_semester.values():
		for officership in officership_semester:
			print officership
			person = matchPerson(officership[0])
			username = officership[1]
			position = matchPosition(officership[2])
			semester = officership[3]
	
			try:
				os = Officership.objects.get(person = person, position = position, semester = semester)
				print "Officership: " + str(os) + " already existed!"
			except Officership.DoesNotExist:
				os = Officership(person = person, position = position, semester = semester)
				os.save()
				g = Group.objects.get(name = position.short_name)
				person.user.groups.add(g)
				if semester == hkn.semester.getCurrentSemester():
					person.member_status = MEMBER_TYPE.OFFICER
				else:
					person.member_status = MEMBER_TYPE.FOGIE
				person.save()
			


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
		p = Position.objects.get(long_name = name.strip())
		return p
	except ObjectDoesNotExist:
		pass

	return None

if __name__ == "__main__":
	import_officers()

