#!/usr/bin/env python
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import re, django
import hkn_settings

from hkn.info.constants import MEMBER_TYPE

from hkn.info.models import *
from hkn.auth.models import *


me = Person.objects.get(first="Hisham")
me.member_status = MEMBER_TYPE.OFFICER
me.save()
u = me.user
u.set_password("monkey")
u.is_superuser = True
u.save()

me = Person.objects.get(first="Vishay")
u = me.user
u.set_password("monkey6969")
u.is_superuser = True
u.save()
