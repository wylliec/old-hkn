#!/usr/bin/env python

def eradicate(user):
    try:
        user.candidateinfo.candidateapplication_set.all().delete()
    except Exception, e:
        print "Got exception %s" % e
    try:
        user.candidateinfo.delete()
    except Exception, e:
        print "Got exception %s" % e
    try:
        user.registrationprofile_set.all().delete()
    except Exception, e:
        print "Got exception %s" % e
    try:
        user.extendedinfo.delete()
    except Exception, e:
        print "Got exception %s" % e
    try:
        user.delete()
    except Exception, e:
        print "Got exception %s" % e

