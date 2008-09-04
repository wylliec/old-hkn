#!/usr/bin/env python2.5
import hkn_settings
from hkn.info.models import Person
from django.db.models import Q

import time, os, sha, re

PASSWD_FILE = "data/fogies.partial.pwd"

def safe_title(fun):
    def st(e):
        if e:
            return e.strip().strip('.').title()
        return ""
    def do_it(*args, **kwargs):
        return map(lambda e: st(e), fun(*args, **kwargs))
    return do_it


names_regex = (
re.compile("(?P<first>[A-Za-z'\-]+)(?: (?P<middle>[A-Za-z'\-\.]+))? (?P<last>[A-Za-z'\-\.]+)"),
re.compile("(?P<last>[A-Za-z'\-]+)"),
)
@safe_title
def get_names(name):
    name = name.split(",")[0]
    for pattern in names_regex:
        m = pattern.match(name)
        if m:
            d=m.groupdict()
            return (d.get("first"), d.get("middle"), d.get("last"))
    return (None, None, None)
    
def handleUser(uname, name):
    first, realfirst, last = get_names(name)
    person = Person.objects.filter(last_name=last).filter(Q(first_name=first) | Q(realfirst=first))
    if len(person) > 1:
        person = person.filter(realfirst=realfirst)
    if len(person) > 1:
        print "Got %s for %s [%s %s %s]" % (str(person), uname, first, realfirst, last)
        return
    elif len(person) == 0:
        print "No match for %s [%s %s %s]!" % (uname, first, realfirst, last)
        return
    person = person[0]
    person.username = uname
    person.save()

def main(passwd_file=PASSWD_FILE):
    for user in file(passwd_file):
        user = user.strip()
        if len(user) == 0:
            continue
        fields = user.split(":")
        uname, name = fields[0], fields[4]
        #print "%s -> %s" % (uname, get_names(uname))
        handleUser(uname, name)

if __name__ == '__main__':
    main()
