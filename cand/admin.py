from django.contrib import admin
from hkn.cand.models import *

class EligibilityListEntryAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_address', 'class_level')
    search_fields = ('first_name', 'last_name', 'email_address')
    list_filter = ('class_level',)

def entry_name(x):
    return "%s %s" % (x.entry.first_name, x.entry.last_name)

def matched_person_name(x):
    return x.person.name if x.person else "<no match>"

def entry_email(x):
    return x.entry.email_address

def matched_person_email(x):
    return ("%s, %s" % (x.person.email, x.person.school_email)) if x.person else "<no match>"
    
def matched_person_category(x):
    return x.person.member_status if x.person else "<no match>"

class ProcessedEligibilityListEntryAdmin(admin.ModelAdmin):
    list_display = (matched_person_name, entry_name, matched_person_email, entry_email, matched_person_category, 'category')
    search_fields = ('person__first_name', 'person__last_name', 'entry__first_name', 'entry__last_name')
    list_filter = ('category',)

admin.site.register(EligibilityListEntry, EligibilityListEntryAdmin)
admin.site.register(ProcessedEligibilityListEntry, ProcessedEligibilityListEntryAdmin)
