from django.db import models
from django.db.models import Q
from django.contrib.auth.models import *
from hkn.event.models import *
from hkn.event.constants import EVENT_TYPE
from hkn.event.rsvp.constants import RSVP_TYPE
from hkn.main.models import HKN
from hkn.info.models import *

from django import forms
from string import atoi
import os

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
    comment = forms.CharField(label = "Anything We Should Know?", required = False, widget=forms.Textarea(attrs={'rows' : 2, 'wrap' : 'virtual'}))
    #transport = forms.IntegerField(label = "Transport (0 for none)", required = False, widget = forms.HiddenInput())
    #rsvp_data = RSVPDataField(label = "Block RSVPs", required = False, widget = forms.MultipleHiddenInput())

