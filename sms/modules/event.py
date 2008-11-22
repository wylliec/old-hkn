from hkn.sms.module_interface import sms_handler, SkipException

from hkn.event.models import *

@sms_handler(r'rsvp me.*')
def rsvp(user, message, match):
    return 'RSVP message'

@sms_handler(r'future events')
def today_events(user, message, match):
    msg = ", ".join(["%s [%d]" % (e.name, e.id) for e in Event.future.all()])
    return "Future events: " + msg

@sms_handler(r"today'?s events")
def today_events(user, message, match):
    msg = ", ".join(["%s [%d]" % (e.name, e.id) for e in Event.today.all()])
    return "Today's events: " + msg

