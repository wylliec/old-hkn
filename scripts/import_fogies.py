#!/usr/bin/env python2.5
import hkn_settings
from hkn.info.models import Person
from django.db.models import Q

import time, os, sha, re

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
def get_names(uname):
	import pwd
	name = pwd.getpwnam(uname)[4].strip()
	name = name.split(",")[0]
	for pattern in names_regex:
		m = pattern.match(name)
		if m:
			d=m.groupdict()
			return (d.get("first"), d.get("middle"), d.get("last"))
	return (None, None, None)
	
def handleUser(uname):
    first, middle, last = get_names(uname)
    person = Person.objects.filter(last_name=last).filter(Q(first_name=first) | Q(realfirst=first))
    if len(person) > 1:
        print "Got %s for %s [%s %s %s]" % (str(person), uname, first, middle, last)
    elif len(person) == 0:
        print "No match for %s [%s %s %s]!" % (uname, first, middle, last)

def main():
	for user in file("data/fogies.partial.pwd"):
		user = user.strip()
		if len(user) == 0:
			continue
		uname = user.split(":")[0]
		#print "%s -> %s" % (uname, get_names(uname))
		handleUser(uname)

if __name__ == '__main__':
	main()
