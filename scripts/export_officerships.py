#!/usr/bin/env python
from django.core.management import setup_environ
import re, django, sys, pickle, glob

import hkn_settings

from hkn.info.models import *
from hkn.info.utils import *
from hkn.event.models import *

officership_filename = "data/officership-all.pkl"


def officershipTuple(os):
    return (os.person.email(), os.person.user.username, os.position.short_name, os.semester)

def export_officers():
    global officership_filename

    officership_by_semester = {}
    for os in Officership.objects.all():
        if not officership_by_semester.has_key(os.semester):
            officership_by_semester[os.semester] = []
        officership_by_semester[os.semester].append(officershipTuple(os))
    f = file(officership_filename, 'w')
    pickle.dump(officership_by_semester, f)

if __name__ == "__main__":
    export_officers()
