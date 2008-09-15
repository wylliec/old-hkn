#!/usr/bin/env python
import setup_settings

from django.db.models import loading
from django.core.management import call_command
from hkn.event.models import *
import pickle, os

FILENAME = "data/events-permissions.pkl"
events = {}

def main():
    os.system("python2.5 ../../manage.py dumpdata event > data/new_events.json")

    for e in Event.objects.all():
        events[e.slug] = (e.view_permission.codename, e.rsvp_permission.codename)
    pickle.dump(events, file(FILENAME, "w"))

if __name__ == "__main__":
    main()
