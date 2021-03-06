#!/usr/bin/env python

import hkn_settings
from django.contrib.sites.models import Site

def main():
    for s in Site.objects.all():
        s.delete()

    s = Site(domain="hkn.eecs.berkeley.edu", name="HKN")
    s.id = 1
    s.save()

if __name__ == "__main__":
    main()

