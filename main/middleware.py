from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


try:
    from hkn.hknsettings import FORCE_LOGIN
except:
    FORCE_LOGIN = False


LAYOUT_KEY = "set_layout"
THEME_KEY = "set_theme"

class LayoutMiddleware(object):
    def process_request(self, request):
        layout = theme = None

        # set_layout
        rpc = request.GET.copy()
        if LAYOUT_KEY in request.GET:
            request.session["layout"] = request.GET.get(LAYOUT_KEY)
            del rpc[LAYOUT_KEY]
        if THEME_KEY in request.GET:
            request.session["theme"] = request.GET.get(THEME_KEY)
            del rpc[THEME_KEY]

        request.GET = rpc
            
        return None

class HknAuthMiddleware(object):
    def process_request(self, request):
        if 'as_user' in request.GET and request.user.is_superuser:
            as_user = request.GET.get('as_user')
            rpc = request.GET.copy()
            del rpc['as_user']
            request.GET = rpc
            user = get_object_or_404(User, username=as_user)
            request.user = user

        if FORCE_LOGIN and request.path.find("login") == -1 and request.user.is_anonymous():
            return HttpResponseRedirect("/login/?next=%s" % request.path)
        return None
