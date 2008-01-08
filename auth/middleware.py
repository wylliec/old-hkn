from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from hkn.auth.models import User

try:
    from hkn.hknsettings import FORCE_LOGIN
except:
    FORCE_LOGIN = False

class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            from hkn.auth.utils import get_user
            request._cached_user = get_user(request)
        return request._cached_user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        

        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.__class__.user = LazyUser()

        # as_user
        if 'as_user' in request.GET and request.user.is_superuser:
            as_user = request.GET.get('as_user')
            rpc = request.GET.copy()
            del rpc['as_user']
            request.GET = rpc
            user = get_object_or_404(User, username = as_user)
            request.user = user
            
        if FORCE_LOGIN and request.path.find("login") == -1 and request.path.find("authenti") == -1 and request.user.is_anonymous():
            return HttpResponseRedirect("/login/?next=%s" % (request.path))

        return None

