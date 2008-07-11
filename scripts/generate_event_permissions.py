#!/usr/bin/env python

import hkn_settings
from django.contrib.auth.models import *
from hkn.event.models import *

perms = ('main.hkn_everyone', 'main.hkn_candidate_plus', 'main.hkn_member_plus', 'main.hkn_officer')
everyone, candidates_plus, members_plus, officer = map(Permission.objects.get_for_name, perms)

view_p  = (everyone, officer)
rsvp_p  = (candidates_plus, members_plus, officer)

import random
for e in list(Event.objects.all()):
    e.view_permission = random.choice(view_p)
    e.rsvp_permission = random.choice(rsvp_p)
    e.save()

