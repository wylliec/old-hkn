#!/bin/sh
../manage.py --noinput reset auth
../manage.py --noinput reset cand
../manage.py --noinput reset course
../manage.py --noinput reset event
../manage.py --noinput reset info
../manage.py --noinput reset request
../manage.py --noinput reset tutor
../manage.py --noinput flush
../manage.py --noinput syncdb
./create_positions.py
echo  'c' | ./import_people.py
echo  'a' | ./import_people.py
./create_superusers.py
./import_events_from_webcal.py
./import_officership_cached.py
./import_usernames_cached.py
./create_random_rsvps.py
./import_seasons.py
./import_courses.py
./import_instructors.py
./import_klasses.py
