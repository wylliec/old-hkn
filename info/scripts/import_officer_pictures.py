#!/usr/bin/env python

"""
Run this script to reimport officer pictures.

It imports from /hkn/files/officerpics/ so add the pictures there first.

It is safe to re-run this on a live instance, it will only import pictures for
officers whose officer picture does not exist
"""


import setup_settings
import os, os.path
from django.conf import settings
from hkn.info.models import Person
from django.core.files.base import ContentFile

def main():
    for off in Person.all_officers.all():
        if off.officer_picture != None:
        #    print "NOT importing picture for %s" % off.username
            continue
        path = os.path.join(settings.MEDIA_ROOT, "officerpics", off.username)
        for ext in (".jpg", ".jpeg", ".gif"):
            f = "%s%s" % (path, ext)
            if os.path.exists(f):
                print "Importing picture for %s" % off.username
                off.save_officer_picture(ContentFile(file(f).read()), ext=ext)
                continue
        print "Could not find picture for %s" % off.username
                
if __name__ == "__main__":
    main()
