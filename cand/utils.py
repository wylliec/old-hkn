from django.db.models import Q

from hkn.cand.models import *
from hkn.info.models import *
from hkn.info.constants import MEMBER_TYPE
from hkn.info.utils import normalize_email

def process_eligibility_entry(entry):
    email, first_name, last_name = normalize_email(entry.email_address), entry.first_name, entry.last_name
    persons = Person.objects.filter(Q(email=email) | Q(school_email=email))
    if len(persons) == 0:
        persons = Person.objects.all()
    elif len(persons) == 1:
        print "Matched email for %s" % email
        if persons[0].member_type >= MEMBER_TYPE.MEMBER:
            return (persons[0], "MEMBER")
        else:
            return (persons[0], "CANDIDATE")
    elif len(persons) > 1:
        assert(False)

    persons = persons.filter(Q(Q(first_name=first_name)|Q(realfirst=first_name))&Q(last_name=last_name))
    if len(persons) == 0:
        print "-- No match for (%s, %s, %s)" % (first_name, last_name, email)
        return (None, "CANDIDATE")
    elif len(persons) == 1:
        print "Matched name %s %s" % (first_name, last_name)
        if persons[0].member_type >= MEMBER_TYPE.MEMBER:
            return (persons[0], "MAYBE_MEMBER")
        else:
            return (persons[0], "MAYBE_CAND")
    else:
        print "-- Too many name matches for %s %s" % (first_name, last_name)
        return (None, "MAYBE_MEMBER")
    return (None, None)

def process_eligibility_list():
    for p in ProcessedEligibilityListEntry.objects.all():
        p.delete()
    for entry in EligibilityListEntry.objects.all():
        (person, category) = process_eligibility_entry(entry)
        ProcessedEligibilityListEntry.objects.create(entry=entry, person=person, category=category)


