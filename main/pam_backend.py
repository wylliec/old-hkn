from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.core.validators import email_re
try:
    from hkn.main import pam
    PAM_DISABLED = False
except:
    PAM_DISABLED = True

class PamBackend:
    def authenticate(self, username=None, password=None):
        if PAM_DISABLED:
            # if we couldn't import the pam module
            return None

        if not (username and password):
            # we need both username and password
            return None

        try:
            user = User.objects.get(username=username)
            if pam.authenticate(str(username), str(password)):
                return user
        except User.DoesNotExist:
            pass
        return None
