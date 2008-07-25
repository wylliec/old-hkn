#!/usr/bin/env python
import random

import hkn_settings
from hkn.info.models import *
from hkn.info.constants import MEMBER_TYPE

def main():
    for person in list(Person.candidates.all()):
        person.privacy['email'] = random.choice((MEMBER_TYPE.CANDIDATE, MEMBER_TYPE.OFFICER))
        person.privacy['phone'] = random.choice((MEMBER_TYPE.CANDIDATE, MEMBER_TYPE.OFFICER, 1000))
        person.save()

if __name__ == "__main__":
    main()
