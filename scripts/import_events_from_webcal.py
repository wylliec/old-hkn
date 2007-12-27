#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django, sys

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.models import *
from hkn.event.models import *

import MySQLdb


def imp_event(r):
	import datetime
	year = r[1]/12
	month = r[1] - (12 * year) + 1
	#print r
	#print month
	day = r[2]
	start_time = r[3]
	end_time = r[-3]
	color = (r[-4] or "").lower()
	
	start = datetime.datetime(year = year, month = month, day = day) + start_time
	end = datetime.datetime(year = year, month = month, day = day) + end_time

	if start > end:
		end = end + datetime.timedelta(days = 1)

	e = Event()
	e.name = r[4].replace('\xE9', 'e')
	e.description = r[5].replace('\xE9', 'e').replace('\x99', "").replace('\x92', "'")
	e.location = "---"
	e.start_time = start
	e.end_time = end

	if color == "#ffff00":
		e.event_type = "CANDMAND"
	elif color == "#ffbbbb":
		e.event_type = "FUN"
	elif color == "#bbffff":
		e.event_type = "COMSERV"
	elif color == "#ffc040":
		e.event_type = "DEPSERV"
	elif color == "#e0e0e0":
		e.event_type = "JOB"
	elif color == "#00ff00":
		e.event_type = "MISC"
	else:
		print "got color: " + color
		e.event_type = "MISC"

	import random
	e.rsvp_transportation_necessary = True
	if random.random() < .2:
		e.rsvp_transportation_necessary = True

	e.rsvp_block_size = 0

	e.rsvp_type = 1
	if e.event_type == "FUN" or e.event_type == "COMSERV" or e.event_type == "DEPSERV":
		e.rsvp_type = 1
	
	some_permission = Permission.objects.all()[0]

	e.view_permission = some_permission
	e.rsvp_permission = some_permission

	print e.name, e.start_time, e.end_time
	
	e.save(gcal = False)

con  = MySQLdb.Connect(host="localhost", user="webcal_read", passwd="3r337", db = "webcal2")
cursor = con.cursor()

sql = "SELECT * FROM EVENTS WHERE MONTH > 24084"
cursor.execute(sql)
res = cursor.fetchall()
for r in res:
	imp_event(r)
	
