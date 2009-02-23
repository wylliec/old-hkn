#!/usr/bin/env python
import datetime, types, time

from django import forms

_MONTHS = [(i, datetime.date(month=i, year=2008, day=1).strftime("%b")) for i in range(1, 12)]

DEFAULT_DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
)


class SplitDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Select(choices=_MONTHS, attrs=attrs),
            forms.Select(choices=((str(i), str(i)) for i in range(1, 31)), attrs=attrs),
            forms.TextInput(attrs={"size": "5"})
        )
        super(SplitDateWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if type(value) in types.StringTypes:
            for format in DEFAULT_DATE_INPUT_FORMATS:
                try:
                    return self.decompress(datetime.date(*time.strptime(value, format)[:3]))
                except ValueError:
                    continue
        elif type(value) == datetime.date:
            return self.decompress(value)
        return super(SplitDateWidget, self).value_from_datadict(data, files, name)

    def decompress(self, value):
        if value:
            return [value.month, value.day, value.year]
        return [None, None, None]

class SplitDateField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=_MONTHS),
            forms.ChoiceField(choices=((str(i), str(i)) for i in range(1, 31))),
            forms.IntegerField(min_value=1900, max_value=2100),
        )
        self.widget = SplitDateWidget()
        super(SplitDateField, self).__init__(fields, *args, **kwargs)


    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] in (None, ''):
            raise forms.ValidationError("Enter a valid month")
        if data_list[1] in (None, ''):
            raise forms.ValidationError("Enter a valid day")
        if data_list[2] in (None, ''):
            raise forms.ValidationError("Enter a valid year")

        return datetime.date(year=int(data_list[2]), day=int(data_list[1]), month=int(data_list[0]))
