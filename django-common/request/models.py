from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from nice_types import QuerySetManager, PickleField

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
    permission = models.ForeignKey(Permission, null=True)
    permission_user = models.ForeignKey(User, null=True, related_name=None)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    confirm_object = generic.GenericForeignKey()

    title = models.CharField(max_length=50)
    description = models.TextField()
    links = PickleField(null = True)
    
    requestor = models.ForeignKey(User, related_name='requests_requested')
    confirmed_by = models.ForeignKey(User, null=True, related_name='requests_confirmed')
    comment = models.CharField(max_length=100)

    submitted = models.DateTimeField(auto_now_add = True)

    class QuerySet(QuerySet):
        def for_user(self, user):
            return self.filter(permission__in = user.get_all_permissions())

        def ft_query(self, query):
            return self

    def set_metainfo(self):
        self.__dict__.update(getattr(self.confirm_object.__class__, REQUEST_OBJECT_METAINFO_ATTR)(self.confirm_object, self))
        self.confirmed = self.get_confirm_object_confirmed()
        
    def get_confirm_object_confirmed(self):
        return getattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_CONFIRM_ATTR))

    def set_confirm_object_confirmed(self, confirm):
        setattr(self.confirm_object, getattr(self.confirm_object.__class__, REQUEST_OBJECT_CONFIRM_ATTR), confirm)

    def set_confirm(self, confirm, comment, confirmed_by = None):
        self.set_confirm_object_confirmed(confirm)
        self.confirm_object.save()

        self.active = False
        self.comment = comment
        self.confirmed_by = confirmed_by
        self.save()
        
    def __str__(self):
        return self.get_request_description()

    def save(self):
        self.set_metainfo()
        super(Request, self).save()

