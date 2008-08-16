from django.db.models import signals
from hkn.event.models import Event

try:
    from hkn.settings import GCAL_ENABLED
except:
    GCAL_ENABLED = False

if GCAL_ENABLED:
    from hkn.gcal import utils

def if_enabled(fn):
    def check_enabled(*args, **kwargs):
        if not GCAL_ENABLED:
            return
        fn(*args, **kwargs)
    return check_enabled

@if_enabled
def event_saved(event):
    if len(event.gcal_id) > 0:
        event.gcal_id = utils.updateEvent(event)
    else:
        event.gcal_id = utils.addEvent(event)

@if_enabled
def event_deleted(event):
    if len(event.gcal_id) > 0:
        utils.deleteEvent(event)

signals.pre_save.connect(event_saved, Event)
signals.post_delete.connect(event_deleted, Event)
