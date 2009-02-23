from django.db.models import signals
from hkn.event.models import Event
from django.conf import settings


GCAL_ENABLED = getattr(settings, 'GCAL_ENABLED', False)

if GCAL_ENABLED:
    from hkn.gcal import gcal_interface

def gcal_sync(event):
    if not GCAL_ENABLED:
        return
    if len(event.gcal_id.strip()) > 0:
        event.gcal_id = gcal_interface.update_event(event)
    else:
        event.gcal_id = gcal_interface.add_event(event)

def event_saved(instance=None, **kwargs):
    if instance:
        gcal_sync(instance)

def event_deleted(instance=None, **kwargs):
    if len(instance.gcal_id.strip()) > 0:
        gcal_interface.delete_event(instance)

if GCAL_ENABLED:
    signals.pre_save.connect(event_saved, Event)
    signals.post_delete.connect(event_deleted, Event)
