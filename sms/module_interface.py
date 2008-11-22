__all__ = ['sms_handler', 'sms_handler_registry', 'SkipException', 'NoHandlerException', 'InvalidPhoneNumberException']

class SkipException(Exception):
    pass

class NoHandlerException(Exception):
    pass

class InvalidPhoneNumberException(Exception):
    pass

import re
from collections import defaultdict
sms_handler_registry = defaultdict(list)

def sms_handler(regex, priority=100, flags = re.I):
    def deco(fn):
        sms_handler_registry[priority].append((re.compile(regex, flags), fn))
        return fn
    return deco

def sms_handler_iter():
    prios = sms_handler_registry.keys()
    prios.sort()
    for prio in prios:
        for item in sms_handler_registry[prio]:
            yield item

def import_module(modname, template):
    fullname = template % modname
    module = __import__(fullname)
    return (modname, reduce(lambda module, name: getattr(module, name), fullname.split(".")[1:], module))

_modules = None
def get_modules():
    global _modules

    if not _modules:
        from hkn.sms import modules
        fn = lambda m: import_module(m, "hkn.sms.modules.%s")
        _modules = dict(map(fn, modules.SMS_MODULES))
    return _modules
get_modules()
