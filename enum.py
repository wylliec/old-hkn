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

