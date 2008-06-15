#!/bin/sh
./clear_database.sh
../manage.py loaddata ../fixtures/all.json
