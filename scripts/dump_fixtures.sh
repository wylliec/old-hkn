#!/bin/sh
../manage.py dumpdata > ../fixtures/all.json
../manage.py dumpdata course > ../fixtures/course.json
../manage.py dumpdata tutor > ../fixtures/tutor.json
