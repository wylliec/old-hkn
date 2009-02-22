#!/usr/bin/env python
import hkn_settings
from django.contrib.auth.models import Group, Permission

default_permissions = {
"everyone" : ("main.hkn_everyone", "info.view_officers"),
"candidates" : ("main.hkn_candidate", "main.hkn_candidate_plus", "info.view_officers", "info.view_candidates"),
"members" : ("main.hkn_member", "main.hkn_member_plus", "main.hkn_candidate_plus", "info.view_officers", "info.view_members"),
"officers" : ("main.hkn_officer", "info.view_candidates", "event.add_event", "event.change_event", "event.delete_event"),
"current_officers" : ("main.hkn_current_officer",),
"Vice President" : ("info.view_restricted",),
"Bridge" : ("photologue.add_gallery", "photologue.add_galleryupload", "photologue.add_photo", "photologue.add_photoeffect", "photologue.add_photosize", "photologue.add_watermark", "photologue.change_gallery", "photologue.change_galleryupload", "photologue.change_photo", "photologue.change_photoeffect", "photologue.change_photosize", "photologue.change_watermark", "photologue.delete_gallery", "photologue.delete_galleryupload", "photologue.delete_photo", "photologue.delete_photoeffect", "photologue.delete_photosize", "photologue.delete_watermark"),
}

def main():
    print "Creating HKN Groups and Permissions"
    for name, value in default_permissions.items():
        g,created = Group.objects.get_or_create(name = name)
        #g = Group.objects.get(name = name)
        for perm in value:
            permission = Permission.objects.get_for_name(perm)
            print "Adding to group %s: %s" % (str(g), str(permission))
            g.permissions.add(permission)

if __name__ == '__main__':
    main()
