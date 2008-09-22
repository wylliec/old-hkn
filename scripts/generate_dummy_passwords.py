#!/usr/bin/env python

import hkn_settings
from hkn.info.models import Person

def main():
    for username in ("hzarka",):
        u = Person.objects.get(username=username)
        u.set_password("monkey")
        u.is_superuser = True
        u.is_staff = True
        u.save()

if __name__ == "__main__":
    main()
