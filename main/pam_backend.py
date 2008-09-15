from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
try:
    from hkn.main import shadow_wrap
    PAM_DISABLED = False
except:
    PAM_DISABLED = True

class PamBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        if PAM_DISABLED:
            # if we couldn't import the pam module
            return None

        if not (username and password):
            # we need both username and password
            return None

        try:
            user = User.objects.get(username=username)
            if shadow_wrap.authenticate(str(username), str(password)):
                return user
        except User.DoesNotExist:
            pass
        return None
