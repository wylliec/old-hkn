#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import *
from django.contrib.auth.models import *

def main():
    for username in ("hzarka", "rzheng", "ackner", "arjun", "gkchou", "bkim", "jyan"):
        me = Person.objects.get(username=username)
        me.is_active = True
        me.is_superuser = True
        me.is_staff = True
        me.save()

if __name__ == '__main__':
    main()
