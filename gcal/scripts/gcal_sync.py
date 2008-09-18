#!/usr/bin/env python


try:
    from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
    from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time

import setup_settings
from hkn.gcal.gcal_interface import add_event, update_event, get_calendar_service
from hkn.gcal.calendars import calendars, NoCalendarFound
from hkn.event.models import *
from hkn.gcal.event_interface import gcal_sync


def print_calendars():
    for calendar in calendars:
        try:
            c = calendar.get_calendar_entry()
            print "'%s', id: %s" % (calendar.title, c.id.text.split("/")[-1])
        except NoCalendarFound:
            print "Calendar '%s' does not exist, you should create" % calendar.title

def delete_calendars():
    for calendar in calendars:
        try:
            calendar.get_calendar_entry()
            calendar.delete()
            print "Calendar '%s' deleted" % calendar.title
        except NoCalendarFound:
            print "Calendar '%s' does not exist, not deleting" % calendar.title
            
    

def create_calendars():
    for calendar in calendars:
        try:
            calendar.get_calendar_entry()
            print "Calendar '%s' already exists, not creating" % calendar.title
        except NoCalendarFound:
            calendar.create()
            print "Calendar '%s' created" % calendar.title

def sync_events():
    events = Event.public.all()
    for event in events:
        print "Working on event: %s" % event.name
        old_gcal_id = event.gcal_id.strip()
        event.save()
        if old_gcal_id == "":
            if event.gcal_id == "":
                print "00"
            else:
                print "01"
        else:
            if event.gcal_id == old_gcal_id:
                print "10"
            else:
                print "11"

def main():
    while True:
        cmd = raw_input("[e]xit, [p]rint calendars, [d]elete calendars, [c]reate calendars, [s]ync events, [a]ll: ").strip().lower()
        if cmd == 'd':
            delete_calendars()
        elif cmd == 'c':
            create_calendars()
        elif cmd == 's':
            sync_events();
        elif cmd == 'p':
            print_calendars()
        elif cmd == 'a':
            delete_calendars()
            create_calendars()
            sync_events()
        elif cmd == 'e':
            import sys
            sys.exit()
        
if __name__ == "__main__":
    main()


