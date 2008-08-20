#!/usr/bin/env python
import setup_settings; setup_settings.setup()
from hkn.event.models import Event
from hkn.gcal.gcal_interface import add_event, update_event

def sync_event(event):
    if len(event.gcal_id.strip()) > 0:
        print "Updating event: %s" % event.name
        event.gcal_id = update_event(event)
    else:
        print "Adding event: %s" % event.name
        event.gcal_id = add_event(event)
    event.save()

def main():
#    for event in Event.objects.all()[:1]:
#        sync_event(event)
    sync_event(Event.objects.get(location__icontains="hisham"))

if __name__ == "__main__":
    main()


