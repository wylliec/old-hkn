
# const pattern from some cookbook
class _const(object):
    class ConstError(TypeError): pass
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError, "can't rebind const (%s)" % name
        self.__dict__[name] = value
    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError, "can't rebind const (%s)" % name
        raise NameError, name
    
HKN = _const()

HKN.SEMESTER = "sp08"