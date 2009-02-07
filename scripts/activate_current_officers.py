#!/usr/bin/env python2.5
import hkn_settings
from hkn.info.models import Officership

def main():
        for os in Officership.objects.for_current_semester():
                p = os.person
                p.is_active = True
                p.save()

if __name__ == "__main__":
        main()
