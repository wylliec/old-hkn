from django.db import models
from django.db.models import Q
from django.contrib.auth.models import *
from hkn.event.models import *
from hkn.event.constants import EVENT_TYPE, RSVP_TYPE
from hkn.main.models import HKN
from hkn.info.models import *

from django import forms
from string import atoi
import os

class PermissionField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class EventForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()
    location = forms.CharField()

    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()

    rsvp_type = forms.ChoiceField(choices = RSVP_TYPE.choices())
    rsvp_block_size = forms.IntegerField(required = False)
    rsvp_transportation_necessary = forms.BooleanField(required = False)

    event_type = forms.ChoiceField(choices = EVENT_TYPE.choices())
    

    #view_permission = forms.ModelChoiceField(queryset = Permission.objects.filter(Q(content_type = ContentType.objects.get_for_model(HKN)) | Q(content_type = ContentType.objects.get_for_model(Position))))
    view_permission = PermissionField(queryset = Permission.objects.filter(content_type = ContentType.objects.get_for_model(HKN), codename__startswith = "hkn_"))
    rsvp_permission = PermissionField(queryset = Permission.objects.filter(content_type = ContentType.objects.get_for_model(HKN), codename__startswith = "hkn_"))


#	gcal_id = forms.CharField(widget = forms.HiddenInput, required = False)

class RSVPDataField(forms.Field):
    num_rsvp_blocks = 0
    def __init__(self, required=True, label = "Time Blocks", initial = (), help_text="", widget = forms.CheckboxSelectMultiple()):
        super(RSVPDataField, self).__init__(required=required, label=label, initial=initial, help_text=help_text, widget=widget)


    def bindEvent(self, event):
        self.num_rsvp_blocks = event.get_num_rsvp_blocks()
        self.widget.choices = [(i, event.get_formatted_time_range_for_block(i)) for i in range(event.get_num_rsvp_blocks())]

    


    def clean(self, value):
        if not isinstance(value, list):
            raise forms.ValidationError, "value is not of type list! " + str(type(value))
        try:
            for v in value:
                if atoi(v) >= self.num_rsvp_blocks:
                    raise forms.ValidationError, "invalid value!"
        except ValueError, e:
            raise forms.ValidationError, "non-integer value!"
        return value


class RSVPForm(forms.Form):
    comment = forms.CharField(label = "Comment", required = False, widget=forms.Textarea())
    #transport = forms.IntegerField(label = "Transport (0 for none)", required = False, widget = forms.HiddenInput())
    #rsvp_data = RSVPDataField(label = "Block RSVPs", required = False, widget = forms.MultipleHiddenInput())

