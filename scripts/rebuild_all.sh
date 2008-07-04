#!/bin/bash

./clear_database.sh

echo 'Importing minimal events fixture'
../manage.py loaddata ../fixtures/events.json

./create_positions.py
echo  'c' | ./import_people.py
echo  'a' | ./import_people.py
./create_superusers.py
./import_officership_cached.py
./import_usernames_cached.py

#echo 'Importing events from webcal'
#./import_events_from_webcal.py
echo 'Creating random RSVPs'
./create_random_rsvps.py

./import_seasons.py
./import_departments.py
./import_courses.py
./import_instructors.py
cd klass/xml && tar xvfj schedules.tbz && cd ../..
./import_klasses.py
./generate_exams.py
./generate_review_problems.py


