from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from nice_types import QuerySetManager

from request.constants import REQUEST_METAINFO_ATTR, REQUEST_OBJECT_CONFIRM_ATTR, REQUEST_OBJECT_COMMENT_ATTR, REQUEST_OBJECT_METAINFO_ATTR

from hkn.auth.models import User, Permission

class RequestManager(QuerySetManager):
    pass

class ActiveRequestManager(RequestManager):
    def get_query_set(self):
        return super(ActiveRequestManager, self).get_query_set().filter(active = True)
    
class InactiveRequestManager(RequestManager):
    def get_query_set(self):
        return super(InactiveRequestManager, self).get_query_set().filter(active  = False)

class Request(models.Model):
    objects = all = RequestManager()
    actives = ActiveRequestManager()
    inactives = InactiveRequestManager()
    
    id = models.AutoField(primary_key = True)
    
    active = models.BooleanField(default = True)
    permission = models.ForeignKey(Permission)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    confirm_object = generic.GenericForeignKey()
    
    requestor = models.ForeignKey(User)
    submitted = models.DateTimeField(auto_now_add = True)

    class QuerySet(QuerySet):
        def for_user(self, user):
            return self.filter(permission__in = user.get_all_permissions())

        def ft_query(self, query):
            return self

    def set_metainfo(self):
        if hasattr(self, REQUEST_METAINFO_ATTR):
            return
        setattr(self, REQUEST_METAINFO_ATTR, True)
        self.__dict__.update(getattr(self.confirm_object.__class__, REQUEST_OBJECT_METAINFO_ATTR)(self.confirm_object, self))
        self.confirmed = self.get_confirm_object_confirmed()
        self.comment = self.get_confirm_object_comment()
        
        
    def get_confirm_object_confirmed(self):
        return getattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_CONFIRM_ATTR))

    def get_confirm_object_comment(self):
        return getattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_COMMENT_ATTR))

    def set_confirm_object_confirmed(self, confirm):
        setattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_CONFIRM_ATTR), confirm)

    def set_confirm_object_comment(self, comment):
        setattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_COMMENT_ATTR), comment)
        
    def set_confirm(self, confirm, comment):
        self.active = False
        self.set_confirm_object_confirmed(confirm)
        self.set_confirm_object_comment(comment)
        self.confirm_object.save()
        self.save()
        
    def __str__(self):
        return self.get_request_description()

def request_confirmation(confirm_object, requestor, permission):
    ctype = ContentType.objects.get_for_model(confirm_object)
    try:
        return Request.objects.get(content_type__id = ctype.id, object_id = confirm_object.id, requestor=requestor, permission=permission)
    except Request.DoesNotExist:
        r = Request(content_type = ctype, object_id = confirm_object.id, requestor=requestor, permission=permission)
        r.save()
    return r


