#!/usr/bin/env python
import setup_settings

from hkn.info.models import Person
from hkn.tutor.models import Availability, Assignment
from hkn.tutor.constants import TUTORING_DAYS, TUTORING_TIMES, CORY, SODA
from hkn.tutor.scheduler import Slot
from nice_types import semester

def do_office(office, user_list, version):
    day_ix = 0
    time_ix = 0
    for username in user_list.split(','):
        username = username.strip()

        time_ix = (time_ix + 1) % len(TUTORING_TIMES)
        if time_ix == 0:
            day_ix = (day_ix + 1) % len(TUTORING_DAYS)
        
        slot = Slot(TUTORING_DAYS[day_ix], TUTORING_TIMES[time_ix], office)
        print "%s -> %s" % (username, str(slot))
        p = Person.objects.get(username=username)
        avail = Availability(person=p, slot=slot, office=office, semester=semester.current_semester(), preference=1)
        ass = Assignment(person=p, slot=slot, office=office, semester=semester.current_semester(), version=version)
        avail.save()
        ass.save()
    

def main():
    soda_list = "sdc, ingrid, sjavdani, davidzeng, richardxia, pearce, adit, saung, gkchou, waynelin, conorh, wsandy, kylim, justinchu, ppyapali"
    cory_list = "aguo, cliffe, judyhoffman, richardxia, sutardja, rzheng, dwong, kmowery, suhaas, rdorrance, arjun, jkotker, siddharth, zwang, sgowda"
    version = Assignment.get_max_version() + 1
    do_office(SODA, soda_list, version)
    do_office(CORY, cory_list, version)

if __name__ == "__main__":
    main()
