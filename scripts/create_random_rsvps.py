#!/usr/bin/env python

import hkn_settings, random

from hkn.info.models import *
from hkn.event.models import *


for p in Person.candidates.all():
	for e in Event.objects.all():
		ra = random.random()
		if ra < .8:
			r = RSVP(person = p, event = e)
			r.transport = 0
			r.comment = ""
			r.vp_comment = ""
			if ra < .65:
				r.vp_confirm = True
			elif ra < .75:
				r.vp_confirm = False
			else:
				r.vp_confirm = None
			r.rsvp_data_pkl = ""
			r.save()

		
	
for p in Person.officers.all():
	for e in Event.objects.all():
		ra = random.random()
		if ra < .8:
			r = RSVP(person = p, event = e)
			r.transport = 0
			r.comment = ""
			r.vp_comment = ""
			r.vp_confirm = None
			r.rsvp_data_pkl = ""
			r.save()

p = Person.objects.get(first = "Hisham")
if not p in Person.officers.all():
	for e in Event.objects.all():
		ra = random.random()
		if ra < .8:
			r = RSVP(person = p, event = e)
			r.transport = 0
			r.comment = ""
			r.vp_comment = ""
			r.vp_confirm = None
			r.rsvp_data_pkl = ""
			r.save()

		
	
