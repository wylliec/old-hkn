#!/usr/bin/env python

import hkn_settings, random

from hkn.info.models import *
from hkn.event.models import *
from request.models import *

def make_rsvp(p, e):
    if True:
        ra = random.random()
        if ra < .3:
            r, created = RSVP.objects.get_or_create(person = p, event = e, transport = 0)

            req = r.request_confirmation()

            if ra < .05:
                if ra < .005:
                    req.set_confirm(False, "")				
                elif ra < .045:
                    req.set_confirm(True, "")				
                else:
                    r.vp_confirm = None
                    r.save()		
                req.save()						

for p in list(Person.candidates.all()):
    for e in list(Event.objects.all()):
        make_rsvp(p, e)
        

for p in list(Person.officers.all()):
    for e in list(Event.objects.all()):
        make_rsvp(p, e)

p = Person.objects.get(first = "Hisham")
if not p in Person.officers.all():
    for e in list(Event.objects.all()):
        make_rsvp(p, e)

        

    

