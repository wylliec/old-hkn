#!/usr/bin/env python
import setup_settings

from hkn.info.models import Person

def main():
    for p in Person.objects.all():
        p.reconcile_status()
        p.save()
    

if __name__ == "__main__":
    main()
