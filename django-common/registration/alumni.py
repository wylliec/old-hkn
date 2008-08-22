from django.core import urlresolvers
from registration.models import RegistrationProfile
import request

def get_alumnus_metainfo(profile, request):
    metainfo = {}

    metainfo['title'] = "Confirm Member"
    metainfo['links'] = [("person", urlresolvers.reverse("person-view", kwargs = {"person_id" : profile.user.person.id})),]
    metainfo['confirmed'] = profile.is_alumnus
    metainfo['description'] = "Confirm that %s is a member of HKN" % profile.user.person.name
    
    return metainfo

request.register(RegistrationProfile, get_alumnus_metainfo, confirmation_attr='is_alumnus')
