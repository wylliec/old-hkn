from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth.models import Permission, AnonymousUser
from django.core.cache import cache

from nice_types.db import QuerySetManager, CachingManager

class HKNManager(QuerySetManager, CachingManager):
    @staticmethod
    def get_cache_key(**kwargs):
        return kwargs['name']
    
    @staticmethod
    def get_cache_value(instance):
        return instance.value
        

class HKN(models.Model):
    properties = objects = HKNManager()
    
    name = models.CharField(unique=True, max_length=30)
    value = models.CharField(max_length=50)
    
    def __str__(self):
        return "%s: %s" % (self.name, self.value)
    __repr__ = __str__

    class QuerySet(QuerySet):
        pass
    
    class Meta:
        permissions = (
            ("hkn_everyone", "Everyone!"),
            ("hkn_candidate_plus", "Candidates, members, and officers!"),
            ("hkn_member_plus", "Members and officers!"),
            ("hkn_officer", "Current and ex-officers!"),
            ("hkn_current_officer", "Current officers only!"),
            ("hkn_candidate", "Candidates only!"),
            ("hkn_member", "Members only!"),
        )
        verbose_name = "Property"
        verbose_name_plural = "Properties"

from hkn.main.auth_extend import *
