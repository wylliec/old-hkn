from hkn.event.models import RSVP
from hkn.auth.models import Permission
from hkn.request.constants import REQUEST_TYPE
from django.core import urlresolvers


def add_rsvp_type_metainfo(request):
    try:
        r = RSVP.objects.get(pk = request.object_id)
    except:
        request.title = ""
        request.description = ""
        return request
    
    request.title = "Confirm RSVP"
    request.description = "Confirm %s's RSVP for %s" % (r.person.name(), r.event.name)
    request.links = {"rsvp" : urlresolvers.reverse("hkn.event.rsvp.rsvp.view", kwargs = {"rsvp_id" : r.id}),
                     "person" : urlresolvers.reverse("hkn.info.person.view", kwargs = {"person_id" : r.person_id}),
                     "event" : urlresolvers.reverse("hkn.event.event.view", kwargs = {"event_id" : r.event_id})}
    request.confirm = r.vp_confirm
    if request.confirm is None:
        request.confirm = "None"
    request.comment = r.vp_comment

    return request

def add_unimplemented_type_metainfo(request):
    request.title = "ERROR :("
    request.description = "Unimplemented for this type!"
    return request

def confirm_rsvp_type(request, confirm, comment):
    r = RSVP.objects.get(pk = request.object_id)
    
    r.vp_confirm = confirm
    r.vp_comment = comment
    r.save()

def confirm_unimplemented_type(request, confirm, comment):
    raise Exception, "Request type unimplemented!"

def request_rsvp_confirmation(r, rsvp, requestor):
    r.type = REQUEST_TYPE.RSVP
    r.permissions = Permission.objects.get(codename = "group_vp")
    r.active = True
    r.requestor = requestor
    r.object_id = rsvp.id
    return r

def request_unimplemented_confirmation(r, object, requestor):
    raise Exception, "unimplemented!"


METAINFO_FUNCTIONS = {
                      REQUEST_TYPE.RSVP : add_rsvp_type_metainfo,
                      REQUEST_TYPE.EXAM : add_unimplemented_type_metainfo,
                      REQUEST_TYPE.RESUME : add_unimplemented_type_metainfo,
                      REQUEST_TYPE.CHALLENGE : add_unimplemented_type_metainfo
                      }

CONFIRM_FUNCTIONS = {
                      REQUEST_TYPE.RSVP : confirm_rsvp_type,
                      REQUEST_TYPE.EXAM : confirm_unimplemented_type,
                      REQUEST_TYPE.RESUME : confirm_unimplemented_type,
                      REQUEST_TYPE.CHALLENGE : confirm_unimplemented_type
                      }        

CREATE_FUNCTIONS = {
                      REQUEST_TYPE.RSVP : request_rsvp_confirmation,
                      REQUEST_TYPE.EXAM : request_unimplemented_confirmation,
                      REQUEST_TYPE.RESUME : request_unimplemented_confirmation,
                      REQUEST_TYPE.CHALLENGE : request_unimplemented_confirmation                    
                    }

PRIMARY_KEYS = {
                      REQUEST_TYPE.RSVP : "id",
                      REQUEST_TYPE.EXAM : None,
                      REQUEST_TYPE.RESUME : None,
                      REQUEST_TYPE.CHALLENGE : None
                    }