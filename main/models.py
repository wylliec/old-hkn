from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Permission, AnonymousUser

# Create your models here.
class HKN(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=50)

    class Meta:
        permissions = (
            ("hkn_everyone", "Everyone!"),
            ("hkn_candidate_plus", "Candidates, members, and officers!"),
            ("hkn_member_plus", "Members and officers!"),
            ("hkn_officer", "Current and ex-officers!"),
            ("hkn_current_officer", "Current officers only!"),
            ("hkn_candidate", "Candidates only!"),
            ("hkn_member", "Members only!"),
        )

class PermissionManager(models.Manager):
    def get_for_name(self, permission_name):
        """
        Takes a name like info.hkn_officer and returns the permission
        """
        app_label, codename = permission_name.split(".")
        return self.get_query_set().get(Q(content_type__app_label = app_label) & Q(codename = codename))

PermissionManager().contribute_to_class(Permission, "objects")
setattr(AnonymousUser, 'get_all_permissions', lambda anonuser: [Permission.objects.get(codename="hkn_everyone").full_codename()])
setattr(Permission, 'full_codename', lambda perm: "%s.%s" % (perm.content_type.app_label, perm.codename))
