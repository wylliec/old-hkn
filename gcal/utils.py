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

def getCalendarEntry(event_type):
	calendar_service = getCalendarService()
	feed = calendar_service.GetOwnCalendarsFeed()
	for cal in feed.entry:
		if cal.title.text == GCAL.calendar_titles[event_type]:
			return cal
	raise Exception, "Could not find calendar for event type: " + event_type

_events_feed_link = {}
def getEventsFeed(event_type):
	global _events_feed_link
	calendar_service = getCalendarService()
	if not event_type in _events_feed_link:
		cal = getCalendarEntry(event_type)
		_events_feed_link[event_type] = cal.GetAlternateLink().href

	return calendar_service.GetCalendarEventFeed(_events_feed_link[event_type])

def getEventsPostUrl(event_type):
	return getEventsFeed(event_type).GetPostLink().href

def getContentForEvent(event):
	return event.description

def getEvent(gcal_event_id):
	calendar_service = getCalendarService()
	return calendar_service.GetCalendarEventEntry(gcal_event_id)

def deleteEvent(event):
	getCalendarService().DeleteEvent(getEvent(event.gcal_id).GetEditLink().href)

def hknExtendedPropertiesFromEvent(event):
	p1 = gdata.calendar.ExtendedProperty(name="hkn_event_id", value=str(event.id))
	p2 = gdata.calendar.ExtendedProperty(name="rsvp_transport_necessary", value=str(event.rsvp_transportation_necessary))
	p3 = gdata.calendar.ExtendedProperty(name="rsvp_type", value=str(event.rsvp_type))
	return (p1, p2, p3)

# 
def updateEvent(event):
	gcal_event = getEvent(event.gcal_id)

	gcal_event.title = atom.Title(text=event.name)
	gcal_event.content = atom.Content(text=getContentForEvent(event))

	gcal_event.where = [gdata.calendar.Where(value_string = event.location)]
	gcal_event.extended_property = list(hknExtendedPropertiesFromEvent(event))

	start_time = event.start_time.strftime("%Y-%m-%dT%H:%M:%S")
	end_time = event.end_time.strftime("%Y-%m-%dT%H:%M:%S")

	gcal_event.when = [gdata.calendar.When(start_time = start_time, end_time = end_time)]

	calendar_service = getCalendarService()
	updated_event = calendar_service.UpdateEvent(gcal_event.GetEditLink().href, gcal_event)

	return updated_event.id.text


def addEvent(event):
	gcal_event = gdata.calendar.CalendarEventEntry()
	gcal_event.title = atom.Title(text=event.name)
	gcal_event.content = atom.Content(text=getContentForEvent(event))
	gcal_event.where.append(gdata.calendar.Where(value_string = event.location))
	gcal_event.extended_property += list(hknExtendedPropertiesFromEvent(event))

	start_time = event.start_time.strftime("%Y-%m-%dT%H:%M:%S")
	end_time = event.end_time.strftime("%Y-%m-%dT%H:%M:%S")

	gcal_event.when.append(gdata.calendar.When(start_time = start_time, end_time = end_time))

	calendar_service = getCalendarService()
	url = getEventsPostUrl(event.event_type)
	new_event = calendar_service.InsertEvent(gcal_event, url)

	return new_event.id.text
