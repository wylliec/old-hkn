from hkn.main.models import HKN
import datetime


class PropertyConst(object):
    """
    A wrapper around doing database queries for HKN properties. Doing something like:
        >>> PROPERTIES.semester
    
    is roughly equivalent to:
        >>> HKN.objects.get(name="semester").value
    
    Also includes some auxillary properties such as year which 
    are not stored as properties themselves, but are derived from stored properties.
    """
    class ConstError(TypeError): pass
    
    @property
    def year(self):
        year = int(self.semester[2:])
        if year < 100:
            if year < 60:
                year += 2000
            else:
                year += 1900
        return year
    
    def __getattr__(self, name):
        try:
            return HKN.objects.get_cached(name=name)
        except HKN.DoesNotExist:
            raise AttributeError, name
        
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError, "can't rebind const (%s)" % name
        self.__dict__[name] = value
        
    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError, "can't rebind const (%s)" % name
        raise NameError, name

PROPERTIES = PropertyConst()
