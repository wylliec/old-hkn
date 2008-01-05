#!/usr/bin/env python

import hkn_settings, random

from hkn.info.models import *
from hkn.event.models import *
from hkn.request.models import *
from hkn.request.constants import REQUEST_TYPE




for p in Person.candidates.all():
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
			
			if ra < .05:
				req = Request.objects.request_confirmation(REQUEST_TYPE.RSVP, r, p)			
				if ra < .005:
					req.set_confirm(False, "")				
				elif ra < .045:
					req.set_confirm(True, "")				
				else:
					r.vp_confirm = None
				req.save()						
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

		
	
