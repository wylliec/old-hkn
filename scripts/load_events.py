#!/usr/bin/env python
import hkn_settings
import pickle, os
from hkn.event.models import *

FILENAME = "data/events-permissions.pkl"

events = pickle.load(file(FILENAME))
def main():
    os.system("python2.5 ../manage.py loaddata ../fixtures/new_events.json")
    for slug, codenames in events.items():
        e = Event.objects.get(slug=slug)
        e.view_permission = Permission.objects.get(codename=codenames[0])
        e.rsvp_permission = Permission.objects.get(codename=codenames[1])
        e.save()

if __name__ == "__main__":
    main()
