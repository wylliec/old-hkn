#!/usr/bin/env python
import setup_settings

from hkn.info.models import Person

from hkn.sms import module_interface

def main(phone_number, message):
    try:
        user = Person.objects.get(phone=phone_number)
    except Person.DoesNotExist:
        raise module_interface.InvalidPhoneNumberException("Bad phone")

    for regex, fn in module_interface.sms_handler_iter():
        try:
            match = regex.match(message)
            if match:
                response = fn(user, message, match)
                break
        except module_interface.SkipException, e:
            pass
    else:
        raise module_interface.NoHandlerException("No handler found for message!")
    
    return fn, response

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print "Usage: %s <phone number> \"<message>\"" % sys.argv[0]
        sys.exit(0)
    phone_number, message = sys.argv[1:3]
    try:
        fn, response = main(phone_number, message) 
        print "%s.%s responds:" % (fn.__module__.split(".")[-1], fn.__name__)
        print ">> '%s'" % response
    except module_interface.InvalidPhoneNumberException:
        print "EXCEPTION: No user found with phone number '%s'" % phone_number
    except module_interface.NoHandlerException:
        print "EXCEPTION: No module responded to message '%s'" % message
    
    
