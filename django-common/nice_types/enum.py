
__all__ = ['Enum', 'EnumValue']

from django.utils.datastructures import SortedDict

class EnumValue( dict ):
    creation_counter = 0

    def __init__(self, value, name, **kwargs):
        kwargs['value'] = value
        kwargs['name'] = name
        self.update(kwargs)
        self.creation_counter = EnumValue.creation_counter
        EnumValue.creation_counter += 1

    def __cmp__(self, other):
        if isinstance(other, EnumValue):
            return cmp(self['value'], other['value'])
        return cmp(self['value'], other)

    def __str__(self):
        return str(self['value'])
    
    def __unicode__(self):
        return unicode(self['value'])

    def __repr__(self):
        return "<EnumValue: %s>" % self['value']

    def __hash__(self):
        return hash(self['value'])

from collections import defaultdict
class DeclarativeEnumMetaclass(type):
    def __new__(cls, name, bases, attrs):
        enumvalues = []
        for field_name, enumvalue in attrs.items():
            if not isinstance(enumvalue, EnumValue):
                continue
            if not enumvalue.has_key('key'):
                enumvalue['key'] = field_name
            enumvalues.append(enumvalue)
            attrs[field_name] = enumvalue['value']

        enumvalues.sort(lambda x, y: cmp(x.creation_counter, y.creation_counter))
        attrs['enums'] = enumvalues

        dicts = defaultdict(SortedDict)
        lists = defaultdict(list)
        for enum in enumvalues:
            keys = enum.keys()
            for k1 in keys:
                lists[k1].append(enum[k1])
                for k2 in keys:
                    if k1 == k2:
                        continue
                    dicts[(k1, k2)][enum[k2]] = enum[k1]
        attrs['dicts'] = dicts
        attrs['lists'] = lists
        for key in lists.keys():
            def method_maker(key):
                return classmethod(lambda cls: cls.lists[key])
            attrs[key + 's'] = method_maker(key)
        for keys, d in dicts.items():
            def method_maker(keys):
                def method(cls, lookup, *args):
                    try:
                        return cls.dicts[keys][lookup]
                    except KeyError:
                        if len(args) > 0:
                            return args[0]
                        raise
                return classmethod(method)
            attrs['get_%s_from_%s' % keys] = method_maker(keys)
        attrs['choices'] = dicts[('name', 'value')].items()

        return super(DeclarativeEnumMetaclass, cls).__new__(cls, name, bases, attrs)

class Enum( object ):
    __metaclass__ = DeclarativeEnumMetaclass
    def __init__(self):
        return
