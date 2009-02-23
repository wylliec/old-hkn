from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils.datastructures import SortedDict

class FieldsetMetaclass(DeclarativeFieldsMetaclass):
    def __new__(cls, clsname, bases, attrs):
        fields_present = set()
        fieldsets = SortedDict()
        fieldset_help = {}

        fieldset_sets = []
        if attrs.has_key('fieldsets'):
            fieldset_sets.append(attrs['fieldsets'])
        fieldset_sets += [clazz.fieldsets for clazz in bases if hasattr(clazz, 'fieldsets')]
        for fieldset in fieldset_sets:
            for values in fieldset:
                if len(values) == 3:
                    name, help_text, fields = values
                    fieldset_help[name] = fieldset_help.get(name, help_text)
                else:
                    name, fields = values
                fields = [f for f in fields if f not in fields_present]
                fields_present.update(fields)
                if not fields:
                    continue

                if fieldsets.has_key(name):
                    fieldsets[name] = fieldsets[name] + fields
                else:
                    fieldsets[name] = fields

        if fieldsets.has_key(None):
            del fieldsets[None]
    
        attrs['fieldsets'] = fieldsets.items()
        attrs['fieldset_help'] = fieldset_help

        return super(FieldsetMetaclass, cls).__new__(cls, clsname, bases, attrs)
