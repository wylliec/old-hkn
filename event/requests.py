from django.core import urlresolvers
from hkn.event.models import RSVP
import request

def get_rsvp_metainfo(rsvp, request):
    metainfo = {}

    metainfo['title'] = "Confirm RSVP"
    metainfo['description'] = "Confirm %s's RSVP for %s" % (rsvp.person.name, rsvp.event.name)
    metainfo['links'] = (("rsvp", urlresolvers.reverse("rsvp-view", kwargs = {"rsvp_id" : rsvp.id})),
                     ("person", urlresolvers.reverse("person-view", kwargs = {"person_id" : rsvp.person_id})),
                     ("event", urlresolvers.reverse("event-view", kwargs = {"event_id" : rsvp.event_id})))
    metainfo['confirmed'] = rsvp.vp_confirm 
    return metainfo

request.register(RSVP, get_rsvp_metainfo, confirmation_attr='vp_confirm')
