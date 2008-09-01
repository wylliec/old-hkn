#!/usr/bin/env python
import glob, sys


import hkn_settings
from hkn.info.models import *
from hkn.info.constants import MEMBER_TYPE

def handleFile(initiates_file):
    import os
    import os.path
    f = file(initiates_file, "r")
    initiates_file = os.path.basename(initiates_file).replace("initiates_", "").replace(".txt", "")
    semester = initiates_file[:-2]
    yr = initiates_file[-2:]
    if semester == "fall":
        semester = "fa"
    elif semester == "spring":
        semester = "sp"
    else:
        print "unknown: " + initiates_file
    semester = semester + yr
    print "Setting initiates from " + semester
    for l in f:
        name = l.strip()
        p = matchPerson(name, semester)
        if p:
#            print "Matched %s" % p.name
            if p.member_type < MEMBER_TYPE.MEMBER:
                p.member_type = MEMBER_TYPE.MEMBER
            p.save()
        else:
            print "Could not match %s" % name

def matchPerson(name, semester):
    names = name.split(" ")
    p = None
    nickname = None
    for n in names:
        n = n.strip()
        if n.startswith("(") and n.endswith(")"):
            nickname = n[1:-1]
    if nickname:
        names.remove("(" + nickname + ")")

    potential_names = []
    if len(names) == 2:
        potential_names.append({"first" : names[0], "last" : names[1]})
    elif len(names) == 3:
        potential_names.append({"first" : names[0] + " " + names[1], "last" : names[2]})
        potential_names.append({"first" : names[0] + "-" + names[1], "last" : names[2]})
        potential_names.append({"first" : names[0], "last" : names[2]})

    for pn in potential_names:
        try:
            p = Person.objects.get(first_name__iexact = pn["first"], last_name__iexact = pn["last"], candidateinfo__candidate_semester = semester)
            break
        except Person.DoesNotExist:
            pass


        try:
            if nickname:
                p = Person.objects.get(first_name__iexact = nickname, last_name__iexact = pn["last"], candidateinfo__candidate_semester = semester)
                break
        except Person.DoesNotExist:
            pass

    return p


def main():
    initiates_files = glob.glob("data/initiates/initiates_*.txt")
    for initiates_file in initiates_files:
        handleFile(initiates_file)

if __name__ == "__main__":
    main()
