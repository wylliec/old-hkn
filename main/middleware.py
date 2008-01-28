from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from hkn.auth.models import User

LAYOUT_KEY = "set_layout"

class LayoutMiddleware(object):
    def process_request(self, request):

        # set_layout
        if 'set_layout' in request.GET:
            layout = request.GET.get(LAYOUT_KEY)
	    rpc = request.GET.copy()
	    del rpc[LAYOUT_KEY]
	    request.GET = rpc
	    request.session["layout"] = layout
            
        return None

