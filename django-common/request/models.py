from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from nice_types.db import QuerySetManager, PickleField

from request.constants import REQUEST_METAINFO_ATTR, REQUEST_OBJECT_CONFIRM_ATTR, REQUEST_OBJECT_COMMENT_ATTR, REQUEST_OBJECT_METAINFO_ATTR

from django.contrib.auth.models import User, Permission

class RequestManager(QuerySetManager):
    def for_user(self, *args, **kwargs):
        return self.get_query_set().for_user(*args, **kwargs)
        
    def ft_query(self, *args, **kwargs):
        return self.get_query_set().ft_query(*args, **kwargs)        

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
            if user.is_anonymous():
                return self.none()
            permission_ids = set([p[0] for p in self.values_list('permission')])
            permissions = Permission.objects.in_bulk(list(permission_ids)).values()
            permissions_codenames = dict((p.full_codename(), p) for p in permissions)
            codenames_set = set(permissions_codenames.keys()) & user.get_all_permissions()
            permissions_set = [permissions_codenames[codename] for codename in codenames_set]

            return self.filter(Q(permission__in = permissions_set) | Q(permission_user = user))

        def ft_query(self, query):
            return self.filter(description__icontains = query)

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
        return self.description

    def save(self):
        self.set_metainfo()
        super(Request, self).save()

