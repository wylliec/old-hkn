#!/usr/bin/env python
import hkn_settings
from django.contrib.auth.models import Group, Permission

default_permissions = {
"everyone" : ("main.hkn_everyone", "info.view_officers"),
"candidates" : ("main.hkn_candidate", "main.hkn_candidate_plus", "info.view_officers", "info.view_candidates"),
"members" : ("main.hkn_member", "main.hkn_member_plus", "main.hkn_candidate_plus", "info.view_officers", "info.view_members"),
"officers" : ("main.hkn_officer", "info.view_candidates", "event.add_event", "event.change_event", "event.delete_event"),
"current_officers" : ("main.hkn_current_officer",),
"group_vp" : ("info.view_restricted",)
}

def main():
    print "Creating HKN Groups and Permissions"
    for name, value in default_permissions.items():
        g, created = Group.objects.get_or_create(name = name)
        for perm in value:
            permission = Permission.objects.get_for_name(perm)
            g.permissions.add(Permission.objects.get_for_name(perm))

if __name__ == '__main__':
    main()
