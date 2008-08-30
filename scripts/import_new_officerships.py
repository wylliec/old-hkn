#!/usr/bin/env python2.5
import glob
import hkn_settings
from hkn.info.models import Person, Position, Officership

def import_officerships(officership_file):
    semester = officership_file.split("/")[-1].replace("officers-", "").replace(".txt", "")
    for record in file(officership_file):
        record = record.strip()
        if len(record) == 0:
            continue
        email, position = record.split(",")
        try:
            p = Person.objects.get(email__istartswith = email)
        except Exception, e:
            print "Error when looking up '%s': %s" % (email, str(e))
        try:
            pos = Position.objects.get(short_name__iexact = position)
        except Exception, e:
            print "Error when looking up '%s': %s" % (position, str(e))
        os, created = Officership.objects.get_or_create(person=p, position=pos, semester=semester)
        if not created:
            print "Record for %s already existed!" % str(os)


def main():
    officership_files = glob.glob("data/new_officerships/officers-*.txt")
    for officership_file in officership_files:
        import_officerships(officership_file)

if __name__ == '__main__':
    main()
