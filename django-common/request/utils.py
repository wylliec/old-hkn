from django.contrib.contenttypes.models import ContentType
from request.models import Request


def request_confirmation(confirm_object, requestor, permission=None, permission_user=None):
    """                         
    confirm_object -- the model object the request will be associated with
    requester -- the user that sent the request
    permission -- request viewable by people with these permissions
    permission_user -- request to be confirmed by this User object 
    """

    if not (permission or permission_user):
        raise Exception('Must define one of permission or permission_user!')

    ctype = ContentType.objects.get_for_model(confirm_object)
    try:
        return Request.objects.get(content_type__id = ctype.id, object_id = confirm_object.id, requestor=requestor, permission=permission, permission_user = permission_user)
    except Request.DoesNotExist:
        r = Request(content_type = ctype, object_id = confirm_object.id, requestor=requestor, permission=permission, permission_user=permission_user)
        r.save()
    return r
