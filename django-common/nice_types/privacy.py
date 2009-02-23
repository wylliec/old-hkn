from django.utils.datastructures import SortedDict
import types

class PrivacyContext(object):
    def __init__(self):
        self.roles = SortedDict()
        self.comparator = cmp
        self.privacy_field = 'privacy'

class RestrictedObject(object):
    def __init__(self, restricted, accessor, context):
        self.restricted = restricted
        self.privacy = getattr(restricted, context.privacy_field, {})
        self.accessor = accessor
        self.context = context

    def blanktype(self, value):
        if type(value) in types.StringTypes:
            return ""
        return "moo"
        #elif isinstance(value, (models.fields.files.ImageFieldFile, Photo)):
        #    return self.BlankImage()

    def __getattr__(self, attr):
        if self.context.comparator(self.accessor, self.privacy.get(attr, None)) > 0:
            return getattr(self.restricted, attr)
        return self.blanktype(getattr(self.restricted, attr))

