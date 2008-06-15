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

