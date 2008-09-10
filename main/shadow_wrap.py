#!/usr/bin/env python
import os

def authenticate(username, password):
    cmd = "/home/django/shadow/wrapper '%s' '%s'" % (username, password)
    ret = os.system(cmd)
    if ret == 0:
        return True
    else:
        return False

#authenticate("", "' && sleep '20")

if __name__ == "__main__":
    import getpass
    if authenticate(getpass.getuser(), getpass.getpass()):
        print "Authenticated"
    else:
        print "Not authenticated"
