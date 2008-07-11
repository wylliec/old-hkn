#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.constants import MEMBER_TYPE
from hkn.info.models import *
from django.contrib.auth.models import *

created = {}
for name in MEMBER_TYPE.names():
    created[name.lower()] = Person.objects.create_person(name.title(), "Example", name.lower(), "tcquest+%s@gmail.com" % name.lower(), getattr(MEMBER_TYPE, name))

