#!/usr/bin/env python

import setup_settings
from hkn.info.models import Person

def main(username):
    try:
        user = Person.objects.get(username=username)
        print "%s's phone is %s" % (username, user.phone)
    except Person.DoesNotExist:
        print "Couldn't find user '%s'" % username

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "usage: %s <username>" % sys.argv[0]
        sys.exit(0)
    main(sys.argv[1])
