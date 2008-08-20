#!/usr/bin/env python
import os

import hkn_settings
from hkn import settings
from hkn.info.constants import MEMBER_TYPE
from django.core.management import call_command

CWD = os.getcwd()

import clear_db; clear_db.main()

call_command('loaddata', '../fixtures/flatpages.json')

import create_positions; create_positions.main()
import create_permissions; create_permissions.main()

import import_people
import_people.import_people("data/info-candidates-sp08.tsv", MEMBER_TYPE.CANDIDATE)
import_people.import_people("data/info-people.tsv", MEMBER_TYPE.EXCANDIDATE)

import import_officership_cached; import_officership_cached.import_officers()
import import_usernames_cached; import_usernames_cached.main()
import create_superusers; create_superusers.main()
import generate_model_users; generate_model_users.main()
import set_initiates; set_initiates.main()
import generate_privacy_settings; generate_privacy_settings.main()


#echo 'Importing events from webcal'
#./import_events_from_webcal.py
call_command('loaddata', '../fixtures/events.json')
print 'Creating random RSVPs'
import generate_random_rsvps; generate_random_rsvps.main()
import generate_event_permissions; generate_event_permissions.main()

import course.scripts; course.scripts.import_all(settings.SERVER_ROOT)
import exam.scripts; exam.scripts.import_all(settings.SERVER_ROOT)

os.chdir(CWD)
import generate_review_problems; generate_review_problems.main()
import import_tutor_data; import_tutor_data.main()
