#!/bin/sh
../manage.py reset --noinput auth
../manage.py reset --noinput cand
../manage.py reset --noinput course
../manage.py reset --noinput event
../manage.py reset --noinput exam
../manage.py reset --noinput info
../manage.py reset --noinput request
../manage.py reset --noinput tutor
../manage.py flush --noinput
../manage.py syncdb --noinput
./create_positions.py
echo  'c' | ./import_people.py
echo  'a' | ./import_people.py
./create_superusers.py
./import_events_from_webcal.py
./import_officership_cached.py
./import_usernames_cached.py
./create_random_rsvps.py
./import_seasons.py
./import_departments.py
./import_courses.py
./import_instructors.py
cd klass/xml && tar xvfj schedules.tbz && cd ../..
./import_klasses.py
./generate_exams.py
