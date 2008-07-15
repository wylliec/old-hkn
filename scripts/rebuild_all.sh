#!/bin/bash

./clear_database.sh


./create_positions.py
./create_permissions.py
echo  'c' | ./import_people.py
echo  'a' | ./import_people.py
./import_officership_cached.py
./import_usernames_cached.py
./create_superusers.py
./generate_model_users.py
./set_initiates.py
./generate_privacy_settings.py


#echo 'Importing events from webcal'
#./import_events_from_webcal.py
echo 'Importing minimal events fixture'
../manage.py loaddata ../fixtures/events.json
echo 'Creating random RSVPs'
./generate_random_rsvps.py
./generate_event_permissions.py


./import_seasons.py
./import_departments.py
./import_courses.py
./import_instructors.py
cd klass/xml && tar xvfj schedules.tbz && cd ../..
./import_klasses.py

./generate_exams.py
./generate_review_problems.py

./import_tutor_data.py
