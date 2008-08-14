#!/usr/bin/env python
import os

import hkn_settings
from hkn.info.constants import MEMBER_TYPE
from django.core.management import call_command

import clear_db; clear_db.main()

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


import import_seasons; import_seasons.main()
import import_departments; import_departments.main()
import import_courses; import_courses.main()
import import_instructors; import_instructors.main()
os.system('cd klass/xml && tar xvfj schedules.tbz && cd ../..')
import import_klasses; import_klasses.main()

import generate_exams; generate_exams.main()
import generate_review_problems; generate_review_problems.main()
import import_tutor_data; import_tutor_data.main()
