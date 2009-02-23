#!/usr/bin/env python
import datetime
from django import forms
from django.conf import settings

OTHER_CHOICE = ("_OTHER", "[Other]")

class OtherSelectWidget(forms.MultiWidget):
    class Media:
        js = (settings.STATIC_URL + 'nice_types/otherchoice.js',)

    def __init__(self, choices, attrs=None):
        self.default_choices = [OTHER_CHOICE] + choices
        self.default_values = [d[0] for d in self.default_choices]
        if not attrs:
            attrs = {'class' : 'vOtherChoice'}
        textattrs = attrs.copy()
        textattrs.update( {'style' : 'display: none; margin-left: 5px;' } )
        widgets = (
            forms.Select(choices=self.default_choices, attrs=attrs),
            forms.TextInput(attrs=textattrs),
        )
        super(OtherSelectWidget,self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if value in self.default_values:
                return [value, ""]
            else:
                return [OTHER_CHOICE[0], value]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        if data.get(name, False):
            for i, subvalue in enumerate(self.decompress(data[name])):
                data['%s_%d' % (name, i)] = subvalue
        ret = super(OtherSelectWidget, self).value_from_datadict(data, files, name)
        return ret

class OtherChoiceField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        self.default_choices = kwargs.pop("choices")
        if callable(self.default_choices):
            self.default_choices = list(self.default_choices())
        self.default_values = [str(d[0]) for d in self.default_choices]

        field_class = kwargs.pop("field_class", forms.CharField)
        if isinstance(field_class, type):
            field_class = field_class()

        all_choices = list(self.default_choices)
        all_choices.append(OTHER_CHOICE)

        fields = (
            forms.ChoiceField(choices=all_choices),
            field_class,
        )
        self.widget = OtherSelectWidget(choices=self.default_choices)

        kwargs['required'] = False
        super(OtherChoiceField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] == OTHER_CHOICE[0]:
            if data_list[1] in (None, ''):
                raise forms.ValidationError("Please enter a valid option in the 'Other' field")
            return data_list[1]
        if str(data_list[0]) not in self.default_values:
            raise forms.ValidationError("Please select a valid option")
        return data_list[0]
