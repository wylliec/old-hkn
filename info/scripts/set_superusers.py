#!/usr/bin/env python
import setup_settings

from hkn.info.models import Person, Position

def main():
    positions = (Position.objects.get(short_name=n) for n in ("compserv", "pres", "vp"))
    for position in positions:
        for officership in position.officership_set.all().for_current_semester():
            officer = officership.person
            officer.is_superuser = True
            officer.save()
    
    

if __name__ == "__main__":
    main()
