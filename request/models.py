from django.db import models
from hkn.request.constants import REQUEST_TYPE
from hkn.auth.models import *
from hkn.request.types import CONFIRM_FUNCTIONS, CREATE_FUNCTIONS, PRIMARY_KEYS

class RequestManager(models.Manager):
    def query(self, query, objects = None):
        if objects == None:
            objects = self.get_query_set()
            
        return objects
    
    def request_confirmation(self, type, object, requestor):
        try:
            r = Request.objects.get(type = type, object_id = object[PRIMARY_KEYS[type]], requestor = requestor)
        except:
            # good
            r = Request()
            return CREATE_FUNCTIONS[type](r, object, requestor)            
        
        return r

    
    def for_user(self, user, objects = None):
        if objects == None:
            objects = self.get_query_set()
            
        return objects.filter(permissions__in = user.get_all_permissions())        
        

class ActiveRequestManager(RequestManager):
    def get_query_set(self):
        return super(ActiveRequestManager, self).get_query_set().filter(active = True)
    
class InactiveRequestManager(RequestManager):
    def get_query_set(self):
        return super(InactiveRequestManager, self).get_query_set().filter(active = False)

# Create your models here.
class Request(models.Model):
    objects = all = RequestManager()
    actives = ActiveRequestManager()
    inactives = InactiveRequestManager()
    
    
    request_id = models.AutoField(primary_key = True)
    
    type = models.IntegerField(choices = REQUEST_TYPE.choices())
    active = models.BooleanField()
    permissions = models.ForeignKey(Permission)
    requestor = models.ForeignKey(Person)
    submitted = models.DateTimeField(auto_now_add = True)
    
    object_id = models.IntegerField()
    
    def set_confirm(self, confirm, comment):
        self.active = False
        CONFIRM_FUNCTIONS[self.type](self, confirm, comment)
        
        