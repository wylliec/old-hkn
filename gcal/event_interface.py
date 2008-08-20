from django.db.models import signals
from hkn.event.models import Event

try:
    from hkn.settings import GCAL_ENABLED
except:
    GCAL_ENABLED = False

if GCAL_ENABLED:
    from hkn.gcal import gcal_interface


def if_enabled(fn):
    def check_enabled(*args, **kwargs):
        if not GCAL_ENABLED:
            return
        fn(*args, **kwargs)
    return check_enabled

@if_enabled
def gcal_sync(event):
    if len(event.gcal_id.strip()) > 0:
        event.gcal_id = gcal_interface.update_event(event)
    else:
        event.gcal_id = gcal_interface.add_event(event)
#setattr(Event, "gcal_sync", gcal_sync)

@if_enabled
def event_saved(instance=None, **kwargs):
    if instance:
        gcal_sync(instance)

@if_enabled
def event_deleted(instance=None, **kwargs):
    if len(instance.gcal_id.strip()) > 0:
        gcal_interface.delete_event(instance)

signals.pre_save.connect(event_saved, Event)
signals.post_delete.connect(event_deleted, Event)
