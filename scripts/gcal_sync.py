#!/usr/bin/env python
import hkn_settings

from hkn.gcal import utils
from hkn.gcal.constants import GCAL
from hkn.event.models import *

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






_calendar_service = None
def getCalendarService():
    global _calendar_service

    if _calendar_service == None:
        _calendar_service = gdata.calendar.service.CalendarService()
        _calendar_service.email = GCAL.email
        _calendar_service.password = GCAL.password
        _calendar_service.source = GCAL.source
        _calendar_service.ProgrammaticLogin()
    return _calendar_service

def getCalendarEntry(calendar_name):
    calendar_service = getCalendarService()
    feed = calendar_service.GetOwnCalendarsFeed()
    for cal in feed.entry:
        if cal.title.text == calendar_name:
            return cal
    raise Exception, "Could not find calendar!"

def deleteCalendars():
    cs = getCalendarService()
    feed = cs.GetOwnCalendarsFeed()
    for entry in feed.entry:
        if not entry.title.text in GCAL.calendar_titles.values():
            continue
        print 'Deleting calendar: %s' % (entry.title.text,)
        cs.Delete(entry.GetEditLink().href)


def createCalendar(name, color):
    print "Creating calendar: %s with color %s" % (name, color)
    cs = getCalendarService()

    cal = gdata.calendar.CalendarListEntry()
    cal.title = atom.Title(text=name)
    cal.summary = atom.Summary(text=name)
    cal.where = gdata.calendar.Where(value_string = "Berkeley, CA")
    cal.color = gdata.calendar.Color(value = color)
    cal.timezone = gdata.calendar.Timezone(value = 'America/Los_Angeles')
    cal.hidden = gdata.calendar.Hidden(value='false')

    new_cal = cs.InsertCalendar(new_calendar = cal)

    print "Setting default permissions to 'read'"
    aclUrl = new_cal.GetAclLink().href
    rule = gdata.calendar.CalendarAclEntry()
    rule.scope = gdata.calendar.Scope(scope_type='default')
    roleValue = "http://schemas.google.com/gCal/2005#%s" % ("read",)
    rule.role = gdata.calendar.Role(value = roleValue)
    new_rule = cs.InsertAclEntry(rule, aclUrl)
    

def printCalendars():
    for etype in GCAL.calendar_titles.keys():
        c = getCalendarEntry(GCAL.calendar_titles[etype])
        print c.id.text.split("/")[-1]

def createCalendars():
    for etype in GCAL.calendar_titles.keys():
        try:
            getCalendarEntry(GCAL.calendar_titles[etype])
        except:
            createCalendar(GCAL.calendar_titles[etype], GCAL.calendar_colors[etype])

def syncEvents():
    events = Event.objects.all()
    for event in events:
        print "Syncing event: " + event.name
        event.gcal_id = utils.addEvent(event)
        event.save()


def main():
    while True:
        cmd = raw_input("[d]elete calendars, [c]reate calendars, [s]ync events, [a]ll: ").lower()
        if cmd == 'd':
            deleteCalendars()
        elif cmd == 'c':
            createCalendars()
        elif cmd == 's':
            syncEvents();
        elif cmd == 'l':
            printCalendars()
        elif cmd == 'a':
            deleteCalendars()
            createCalendars()
            syncEvents()
        


if __name__ == "__main__":
    main()


