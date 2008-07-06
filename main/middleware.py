from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from hkn.auth.models import User

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

