from hkn.gcal import utils
def eventSaved(event):
    if len(event.gcal_id) > 0:
        event.gcal_id = utils.updateEvent(event)
    else:
        event.gcal_id = utils.addEvent(event)
        


def eventDeleted(event):
    if len(event.gcal_id) > 0:
        utils.deleteEvent(event)
