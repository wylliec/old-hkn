#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import *
from django.contrib.auth.models import *


me = Person.objects.get(username="hzarka")
me.member_type = MEMBER_TYPE.OFFICER
me.set_password("monkey")
me.is_superuser = True
me.is_staff = True
me.save()

me = Person.objects.get(username="vishay")
me.set_password("monkey6969")
me.is_superuser = True
me.is_staff = True
me.save()
