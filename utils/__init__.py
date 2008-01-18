"""
has a default value instead of throwing an error
allows for useful behavior of [] operations
Default value is False
-Darren Lo
"""
class NiceDict(dict):
    def __init__(self, defaultValue = False, *a, **kw):
        self.defaultValue = defaultValue
        dict.__init__(self, *a, **kw)
    
    def __missing__(self, key):
        return self.defaultValue
    
    def copy(self):
        return self.__copy__(self)
    
    def __copy__(self):
        return type(self)(self.defaultValue, self)
    
    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.defaultValue,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'NiceDict(%s, %s)' % (self.defaultValue,
                                        dict.__repr__(self))

"""
a list that also can have a name.  If copied, returns a normal list.
"""
class NamedList(list):
    def __init__(self, name=None, *a, **kw):
        self.name = name
        list.__init__(self, *a, **kw)
    def __repr__(self):
        return 'NamedList(%s, %s)' % (self.name,
                                      list.__repr__(self))