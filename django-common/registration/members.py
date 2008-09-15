from django.core import urlresolvers
from registration.models import RegistrationProfile
import request

def get_member_metainfo(profile, request):
    metainfo = {}

    metainfo['title'] = "Confirm Member"
    metainfo['links'] = [("person", urlresolvers.reverse("person-view", kwargs = {"person_id" : profile.user.person.id})),]
    metainfo['confirmed'] = profile.is_member
    metainfo['description'] = "Confirm that %s is a member of HKN" % profile.user.person.name
    
    return metainfo

request.register(RegistrationProfile, get_member_metainfo, confirmation_attr='is_member')
