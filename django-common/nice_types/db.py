from django.db import models
import pickle

class PickleField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        try:
            return pickle.loads(str(value))
        except:
            return value

    def get_db_prep_save(self, value):
        return pickle.dumps(value)

class QuerySetManager(models.Manager):
    def get_query_set(self):
        return self.model.QuerySet(self.model)

