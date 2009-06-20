from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django import forms

from hkn.main.models import HKN
from hkn.event.models import Event

class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event

    def clean(self):
        if 'end_time' in self.cleaned_data and 'start_time' in self.cleaned_data and self.cleaned_data['end_time'] < self.cleaned_data['start_time']:
            raise forms.ValidationError("End date can't be earlier than start date")
        return self.cleaned_data

class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('name', 'location', 'start_time', 'end_time')
    fieldsets = (
        ('Basic', {'fields' : ('name', 'location', 'description', 'start_time', 'end_time', 'event_type')}),
        ('RSVP Information', {'fields' : ('rsvp_type', 'rsvp_block_size',  'rsvp_transportation_necessary')}),
        ('Access Information', {'fields' : ('view_permission', 'rsvp_permission')})
        )

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EventAdmin, self).formfield_for_dbfield(db_field, **kwargs) 
        if db_field.name.endswith('_permission'): 
            field.queryset = Permission.objects.filter(content_type = ContentType.objects.get_for_model(HKN), codename__startswith = "hkn_")
        return field

admin.site.register(Event, EventAdmin)
