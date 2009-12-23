from django.shortcuts import render_to_response
from hkn.event.models import Event
import datetime
def ics(request):
    """
    This view generates an iCal file from the hkn calendar.
    """
    events = Event.public.all()
    r = render_to_response("calendar/hkn.ics", {'events' : events, 'today':datetime.datetime.now()}, mimetype="text/calendar")
    r['Content-Disposition'] = 'inline; filename=hkn.ics'
    r.content = r.content.replace("\n", "\r\n")
    return r
