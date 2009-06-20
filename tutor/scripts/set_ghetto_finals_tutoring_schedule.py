#!/usr/bin/env python
import setup_settings

from hkn.info.models import Person
from hkn.tutor.models import Availability, Assignment, make_slot
from hkn.tutor.constants import TUTORING_DAYS, TUTORING_TIMES, CORY, SODA
from hkn.tutor.scheduler import Slot
from nice_types import semester

def do_office(office, user_list, version):
    day_ix = -1
    time_ix = -1
    for username in user_list.split(','):
        username = username.strip()

        time_ix = (time_ix + 1) % len(TUTORING_TIMES)
        if time_ix == 0:
            day_ix = (day_ix + 1) % len(TUTORING_DAYS)
        
        slot = make_slot(TUTORING_DAYS[day_ix], TUTORING_TIMES[time_ix])
        p = Person.objects.get(username=username)
        [a.delete() for a in Availability.objects.for_current_semester().filter(person=p)]
#        if Availability.objects.for_current_semester().filter(person=p).count() > 0:
#            print "X %s -> %s %s" % (username, str(slot), office)
#            continue
#        else:
        print "%s -> %s %s" % (username, str(slot), office)
        avail = Availability(person=p, slot=slot, office=office, semester=semester.current_semester(), preference=1)
        avail.save()
        ass = Assignment(person=p, slot=slot, office=office, semester=semester.current_semester(), version=version)
        ass.save()
    

def main():

    soda_list = "richardxia, jkotker, arjun, kylim, zwang, conorh, waynelin, rniwa, davidzeng, justinchu, adit, brlam, mmatloob, saung, tmagrino"    
    cory_list = "namdoh, ibrahima, ingrid, siddharth, jhoffman, sjavdani, anthonychen, kathytang, hjiang, saralv, cphsu, zhangz, tonydear, andrewlee, pssandhu"

    version = Assignment.get_max_version() + 1
    do_office(SODA, soda_list, version)
    do_office(CORY, cory_list, version)
    print "Version is: %s" % version

if __name__ == "__main__":
    main()
