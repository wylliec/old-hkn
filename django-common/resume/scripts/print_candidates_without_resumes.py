#!/usr/bin/env python
import setup_settings
from hkn.info.models import *
from resume.models import *
from nice_types import semester

def main():
    a = set(Person.candidates.all()) - set([r.person for r in Resume.objects.filter(submitted__gte = semester.current_semester().start_date)])
    return a

if __name__ == "__main__":
    print "\n".join(sorted([b.name for b in main()]))

