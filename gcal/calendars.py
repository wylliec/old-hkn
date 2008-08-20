import gdata.calendar.service
import gdata.service
import gdata.calendar
import atom, atom.service

from hkn.event.constants import EVENT_TYPE
from hkn.constants import _const
from hkn.gcal.gcal_interface import get_calendar_service

__all__ = ["calendars", "NoCalendarFound", "CalendarAlreadyExists"]

class NoCalendarFound(Exception):
    pass

class CalendarAlreadyExists(Exception):
    pass

class Calendar(object):
    def __init__(self, title, color, predicate):
        self.predicate, self.title, self.color = predicate, title, color
        self.flush()


    def flush(self):
        self._events_feed_link = None
        self._events_feed = None
        self._calendar_entry = None

    def get_calendar_entry(self):
        if not self._calendar_entry:
            calendar_service = get_calendar_service()
            feed = calendar_service.GetOwnCalendarsFeed()
            for calendar in feed.entry:
                if calendar.title.text == self.title:
                    self._calendar_entry = calendar
                    return self._calendar_entry
            raise NoCalendarFound("Could not find entry for calendar '%s'" % self.title)
        return self._calendar_entry

    def get_events_feed(self):
        if not self._events_feed_link:
            self._events_feed_link = self.get_calendar_entry().GetAlternateLink().href
        if not self._events_feed:
            calendar_service = get_calendar_service()
            self._events_feed = calendar_service.GetCalendarEventFeed(self._events_feed_link)
        return self._events_feed
    
    def get_events_post_url(self):
        return self.get_events_feed().GetPostLink().href

    def delete(self):
        calendar = self.get_calendar_entry()
        calendar_service = get_calendar_service()
        calendar_service.Delete(calendar.GetEditLink().href)
        self.flush()

    def _set_readonly(self):
        calendar = self.get_calendar_entry()
        aclUrl = calendar.GetAclLink().href
        rule = gdata.calendar.CalendarAclEntry()
        rule.scope = gdata.calendar.Scope(scope_type='default')
        roleValue = "http://schemas.google.com/gCal/2005#%s" % ("read",)
        rule.role = gdata.calendar.Role(value = roleValue)

        calendar_service = get_calendar_service()
        new_rule = calendar_service.InsertAclEntry(rule, aclUrl)


    def create(self):
        try:
            calendar = self.get_calendar_entry()
            raise CalendarAlreadyExists("Calendar '%s' already exists!" % (self.title))
        except NoCalendarFound:
            pass
        calendar = gdata.calendar.CalendarListEntry()
        calendar.title = atom.Title(text=self.title)
        calendar.summary = atom.Summary(text=self.title)
        calendar.where = gdata.calendar.Where(value_string = "Berkeley, CA")
        calendar.color = gdata.calendar.Color(value = self.color)
        calendar.timezone = gdata.calendar.Timezone(value = 'America/Los_Angeles')
        calendar.hidden = gdata.calendar.Hidden(value='false')

        calendar_service = get_calendar_service()
        self._calendar_entry = calendar_service.InsertCalendar(new_calendar = calendar)
        self._set_readonly()
        return self._calendar_entry


def is_public(event):
    return event.view_permission.full_codename() == "main.hkn_everyone"

def event_type_predicate(event_type):
    def predicate(event):
        return event.event_type == event_type and is_public(event)
    return predicate
    
calendars = [
Calendar("HKN Events", "#CC3333", is_public),
Calendar("HKN Candidate Mandatory Events", "#CC3333", event_type_predicate(EVENT_TYPE.CANDMAND)),
Calendar("HKN Fun Events", "#3366CC", event_type_predicate(EVENT_TYPE.FUN)),
Calendar("HKN Big Fun Events", "#94A2BE", event_type_predicate(EVENT_TYPE.BIGFUN)),
Calendar("HKN Community Service Events", "#994499", event_type_predicate(EVENT_TYPE.COMSERV)),
Calendar("HKN Departmental Service Events", "#994499", event_type_predicate(EVENT_TYPE.DEPSERV)),
Calendar("HKN Professional Development Events", "#22AA99", event_type_predicate(EVENT_TYPE.JOB)),
Calendar("HKN Miscellaneous Events", "#109618", event_type_predicate(EVENT_TYPE.MISC)),
]
