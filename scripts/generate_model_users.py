#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
import re, django
import hkn_settings

from hkn.info.constants import MEMBER_TYPE
from hkn.info.models import *
from django.contrib.auth.models import *

lion_gif_content = file('lion.gif', 'rb').read()

def main():
    created = {}
    for name in MEMBER_TYPE.names():
        person = Person.objects.create_person(name.title(), "Example", name.lower(), "tcquest+%s@gmail.com" % name.lower(), getattr(MEMBER_TYPE, name))
        lion_gif = SimpleUploadedFile(person.username + ".gif", lion_gif_content)
        person.profile_picture.save(person.generate_filename(lion_gif.name), lion_gif)
        created[name.lower()] = person

if __name__=="__main__":
    main()
