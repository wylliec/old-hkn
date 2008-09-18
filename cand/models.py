from django.db import models
from django.db.models.query import QuerySet
import nice_types.semester
from nice_types.db import QuerySetManager

from hkn.info.models import Person

class EligibilityListEntryManager(QuerySetManager):
    def for_current_semester(self, *args, **kwargs):
        return self.get_query_set().for_current_semester(*args, **kwargs)

class EligibilityListEntry(models.Model):
    objects = EligibilityListEntryManager()
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=10)
    major = models.CharField(max_length=10)
    email_address = models.EmailField(max_length=100)
    local_street1 = models.CharField(max_length=200)
    local_street2 = models.CharField(max_length=200)
    local_city = models.CharField(max_length=100)
    local_state = models.CharField(max_length=30)
    local_zip = models.CharField(max_length=30)
    class_level = models.CharField(max_length=30)
    semester = nice_types.semester.SemesterField()

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class QuerySet(QuerySet):
        def for_current_semester(self):
            return self.filter(semester=nice_types.semester.current_semester())

CATEGORIES = (("CANDIDATE", "Candidate"), ("MAYBE_CAND", "Maybe candidate"), ("MAYBE_MEMBER", "Maybe member"), ("MEMBER", "Member"))
class ProcessedEligibilityListEntry(models.Model):
    entry = models.OneToOneField(EligibilityListEntry)
    person = models.ForeignKey(Person, null=True)
    category = models.CharField(choices=CATEGORIES, max_length=30)

from hkn.cand.admin import *
