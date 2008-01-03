#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys
import hkn_settings
from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import *
from hkn.auth.models import *
from hkn.info.utils import *

DEFAULT_PASSWORD = "password"


def import_people(filename, member_status):
	print "Importing from file: " + filename
	print "Member status: " + MEMBER_TYPE[member_status]
	f = file(filename, 'r')
	for line in f:
		addLine(line, member_status)

def addLine(line, member_status):
	(first, last, realfirst, cand_com, email, lp, pp, la, pa, sid, gradsem, candsem) = line.split("\t")
	c = Person()
	c.first = first.strip()
	c.last = last.strip()
	c.realfirst = realfirst.strip()

	email = normalizeEmail(email)
	if email.find("berkeley.edu") == -1:
		c.preferred_email = email
	else:
		c.school_email = email
	
	c.member_status = member_status
	c.save()

	ci = ExtendedInfo()
	ci.local_phone = normalizePhone(lp)
	ci.perm_phone = normalizePhone(pp)
	ci.local_addr = la.strip()
	ci.perm_addr = pa.strip()
	ci.sid = sid.strip()
	ci.grad_semester = gradsem.strip()
	ci.person = c
	ci.save()

	candidateinfo = CandidateInfo()
	candidateinfo.person = c
	candidateinfo.candidate_semester = candsem.strip()

	com = normalizeCommitteeName(cand_com)
	if com == "":
		print "Could not match committee: " + cand_com
	candidateinfo.candidate_committee = Position.objects.get(short_name = com)
	candidateinfo.comment = ""
	candidateinfo.initiated = False
	candidateinfo.person = c
	candidateinfo.save()

	

	addUser(c)

everyoneGroup = Group.objects.get(name = "everyone")
candidatesGroup = Group.objects.get(name = "candidates")

def addUser(person):
	pw = person.extendedinfo.sid
	if len(pw) == 0:
		pw = person.email().split("@")[0]
	uname = (str(person.first[0]) + person.last).lower()
	count = 0
	while not User.objects.isValidUsername(uname):
		count += 1
		uname = uname + str(count)

	#user = User.objects.create_user(person, uname, pw)
	import datetime
	now = datetime.datetime.now()
	user = User(person = person, username = uname)
	user.user_created = now
	user.last_login = now
	user.setPassword(DEFAULT_PASSWORD)
	user.is_superuser = False
	user.is_active = True
	user.pam_login = False

	user.force_password_change = True
	user.force_info_update = True
	user.groups.add(everyoneGroup)
	if person.member_status == 2:
		user.groups.add(candidatesGroup)
		
	user.save()
	

if __name__ == "__main__":
	w = raw_input("Which data set to import? 'c' for candidates, anything else for other: ")
	if w.strip() == "c":
		import_people("data/info-candidates.tsv", MEMBER_TYPE.CANDIDATE)
	else:
		import_people("data/info-people.tsv", MEMBER_TYPE.EXCANDIDATE)
