#!/usr/bin/env python2.5
import os

import hkn_settings
from hkn import settings
from hkn.info.constants import MEMBER_TYPE
from django.core.management import call_command

os.system("python2.5 clean_pyc.py")

a = raw_input("Can't clear database--use reset_website_db.sh in the /hkn/ directory if that's what you want; enter to continue ")

call_command('syncdb')

import create_sites; create_sites.main()
call_command('loaddata', '../fixtures/flatpages.json')

print 'Adding photo sizes'
import photologue.scripts.create_sizes; photologue.scripts.create_sizes.main()

import create_properties; create_properties.main()
import create_positions; create_positions.main()
import create_permissions; create_permissions.main()

import import_people
import_people.import_people("data/info-people.tsv", MEMBER_TYPE.EXCANDIDATE)

import import_fogie_usernames; import_fogie_usernames.main()
import import_officership_cached; import_officership_cached.import_officers()
import import_new_officerships; import_new_officerships.main()
import create_superusers; create_superusers.main()
import set_initiates; set_initiates.main()

#print 'Importing events'
#call_command('loaddata', '../fixtures/events.json')
#./import_events_from_webcal.py

print 'Importing courses'
call_command('loaddata', '../fixtures/course.json')
#os.system("python2.5 run_course_scripts.py")

print "Importing tutor data"
call_command('loaddata', '../fixtures/tutor.json')
#import import_tutor_data; import_tutor_data.main()


