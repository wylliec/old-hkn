#!/usr/bin/env python
import hkn_settings
import os, os.path
from django.conf import settings
from hkn.info.models import Person
from django.core.files.base import ContentFile

def main():
    for off in Person.all_officers.all():
        path = os.path.join(settings.IMAGES_PATH, "officerpics", off.username)
        for ext in (".jpg", ".jpeg", ".gif"):
            f = "%s%s" % (path, ext)
            if os.path.exists(f):
                off.save_officer_picture(ContentFile(file(f).read()), ext=ext)
                
if __name__ == "__main__":
    main()
