from django.db import models
import pickle, types

class PickleField(models.TextField):
    __metaclass__ = models.SubfieldBase
    PICKLE_PREFIX = "PICKLED::"

    def to_python(self, value):
        try:
            if value.startswith(PickleField.PICKLE_PREFIX):
                return pickle.loads(str( value[len(PickleField.PICKLE_PREFIX):] ))
        except:
            pass
        return value

    def get_db_prep_value(self, value):
        if type(value) in types.StringTypes and value.startswith(PickleField.PICKLE_PREFIX):
            return value
        return PickleField.PICKLE_PREFIX + pickle.dumps(value)


class QuerySetManager(models.Manager):
    def get_query_set(self):
        return self.model.QuerySet(self.model)

class CachingManager(models.Manager):
    _cache = {}
    def get_cached(self, **kwargs):
        cls = self.__class__
        key = cls.get_cache_key(**kwargs)
        try:
            return cls._cache[key]
        except KeyError:
            cls._cache[key] = cls.get_cache_value( self.get_query_set().get(**kwargs) )
            return cls._cache[key]
    
    @classmethod    
    def clear_cache(cls):
        cls._cache.clear()
        
    @staticmethod
    def get_cache_value(instance):
        return instance        
