from django.db import models

class QuerySetManager(models.Manager):
    def get_query_set(self):
        return self.model.QuerySet(self.model)


"""
has a default value instead of throwing an error
allows for useful behavior of [] operations
Default defaultvalue is False
To instantiate by copying another dictionary, you must specify the defaultValue:
  NiceDict(defaultValue="default value", {"example":True})
  
Also allows reversing a dictionary with all distinct values using reverse method
-Darren Lo
"""
class NiceDict(dict):
    def __init__(self, defaultValue = False, *a, **kw):
        self.defaultValue = defaultValue
        dict.__init__(self, *a, **kw)
    
    """
    reverses a NiceDict so that values map to keys, does not gracefully handle
    non-unique values
    """
    def invertedCopy(self):
        ret = NiceDict(self.defaultValue)
        for key in self:
            if self[key] in ret:
                raise 'Duplicate value "' + self[key] + '", cannot invert!'
            ret[self[key]] = key
        return ret
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)
    
    def __missing__(self, key):
        return self.defaultValue
    
    def copy(self):
        return self.__copy__()
    
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
"""
queryDict is annoying.  request.POST and request.GET are examples of queryDict.
Use this wrapper to access a queryDict as if it were a dictionary
with a default value.  This is just syntactic sugar.
ugly: request.POST.get(key, defaultValue)
nice: wrapper[key]
"""
class QueryDictWrapper:
    def __init__(self, queryDict, defaultValue = False):
        self.defaultValue = defaultValue
        self.data = queryDict
    def __getitem__(self, key):
        return self.data.get(key, self.defaultValue)
    def __contains__(self, key):
        return key in self.data
    def getlist(self, key):
        return self.data.getlist(key)


class EnumType( object ):
    """
    Enumerated-values class.
    
    Allows reference to enumerated values by name
    or by index (i.e., bidirectional mapping).
    """
    def __init__( self, **names ):
        # Remember names list for reference by index
        self._names = dict(names)
        self._descriptions = {}
        # Attributes for direct reference
        for _n, _v in self._names.items():
            setattr( self, _n, _v )
    
    def __contains__( self, item ):
        try:
            trans = self[item]
            return True
        except:
            return False
    
    def __iter__( self ):
        return self._names.keys()
    
    def __getitem__( self, key ):
        return self._descriptions[key]
    
    def __len__( self ):
        return len(self._names)
    
    def items( self ):
        return self._names.items()
    
    def choices( self ):
        return self._descriptions.items()
    
    def names( self ):
        return self._names.keys()

    def values( self ):
        return self._names.values()
    
    def add_descriptions(self, descriptions_list):
        for value, description in descriptions_list:
            self._descriptions[value] = description
            
    def describe(self, name):
        return self[self._nameToEnum(name)]        
    
    def _nameToEnum( self, name ):
        try:
            return getattr( self, name )
        except ValueError, exc:
            args = list(exc.args)
            args.append( "Unknown enum value name '%s'" % name )
            args = tuple(args)
            exc.args = args
            raise

    def __str__(self):
        return self._names.__str__()

