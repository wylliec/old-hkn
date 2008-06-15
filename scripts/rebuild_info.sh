#!/bin/sh

./create_positions.py
echo  'c' | ./import_people.py
echo  'a' | ./import_people.py
./create_superusers.py
./import_officership_cached.py
./import_usernames_cached.py

