#!/usr/bin/env python
from hkn.gcal.constants import GCAL

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


__all__ = ["get_calendar_service", "add_event", "update_event"]

_calendar_service = None
def get_calendar_service():
    global _calendar_service

    if _calendar_service == None:
        _calendar_service = gdata.calendar.service.CalendarService()
        _calendar_service.email = GCAL.email
        _calendar_service.password = GCAL.password
        _calendar_service.source = GCAL.source
        _calendar_service.ProgrammaticLogin()
    return _calendar_service

from hkn.gcal.calendars import calendars

def get_calendars_for_event(event):
    return filter(lambda calendar: calendar.predicate(event), calendars)

def get_gcal_events(event):
    calendar_service = get_calendar_service()
    gcal_ids = event.gcal_id.split(":::")
    events = [calendar_service.GetCalendarEventEntry(gcal_id) for gcal_id in gcal_ids]
    return events

def delete_gcal_event(event):
    calendar_service = get_calendar_service()
    for gcal_event in get_gcal_events(event):
        calendar_service.DeleteEvent(gcal_event.GetEditLink().href)

def hkn_extended_properties_from_event(event):
    p1 = gdata.calendar.ExtendedProperty(name="hkn_event_id", value=str(event.id))
    p2 = gdata.calendar.ExtendedProperty(name="rsvp_transport_necessary", value=str(event.rsvp_transportation_necessary))
    p3 = gdata.calendar.ExtendedProperty(name="rsvp_type", value=str(event.rsvp_type))
    return (p1, p2, p3)


def populate_gcal_event(event, gcal_event):
    gcal_event.title = atom.Title(text=event.name)
    gcal_event.content = atom.Content(text=event.description)

    gcal_event.where = [gdata.calendar.Where(value_string = event.location)]
    gcal_event.extended_property = list(hkn_extended_properties_from_event(event))

    start_time = event.start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_time = event.end_time.strftime("%Y-%m-%dT%H:%M:%S")

    gcal_event.when = [gdata.calendar.When(start_time = start_time, end_time = end_time)]
    return gcal_event


def update_event(event):
    calendar_service = get_calendar_service()
    ids = []
    for gcal_event in get_gcal_events(event):
        gcal_event = populate_gcal_event(event, gcal_event)
        updated_event = calendar_service.UpdateEvent(gcal_event.GetEditLink().href, gcal_event)
        ids.append(updated_event.id.text)
    return ":::".join(ids)

def add_event(event):
    gcal_event = gdata.calendar.CalendarEventEntry()
    gcal_event = populate_gcal_event(event, gcal_event)

    calendar_service = get_calendar_service()
    calendars = get_calendars_for_event(event)
    ids = []
    for calendar in calendars:
        new_event = calendar_service.InsertEvent(gcal_event, calendar.get_events_post_url())
        ids.append(new_event.id.text)
    return ":::".join(ids)


