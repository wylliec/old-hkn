#!/usr/bin/env python
import os

import hkn_settings
from hkn import settings
from hkn.info.constants import MEMBER_TYPE
from django.core.management import call_command

import clear_db; clear_db.main()

import create_sites; create_sites.main()
call_command('loaddata', '../fixtures/flatpages.json')

import create_positions; create_positions.main()
import create_permissions; create_permissions.main()

import import_people
import_people.import_people("data/info-candidates-sp08.tsv", MEMBER_TYPE.CANDIDATE)
import_people.import_people("data/info-people.tsv", MEMBER_TYPE.EXCANDIDATE)

import import_officership_cached; import_officership_cached.import_officers()
import import_usernames_cached; import_usernames_cached.main()
import create_superusers; create_superusers.main()
import set_initiates; set_initiates.main()

print 'Importing events'
#./import_events_from_webcal.py
call_command('loaddata', '../fixtures/events.json')
os.system("python run_generate_scripts.py")
os.system("python run_course_scripts.py")
os.system("python run_exam_scripts.py")

import generate_review_problems; generate_review_problems.main()
import import_tutor_data; import_tutor_data.main()
