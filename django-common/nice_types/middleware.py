from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class AsUserMiddleware(object):    
    def process_request(self, request):
        if 'as_user' in request.GET and request.user.is_superuser:
            as_user = request.GET.get('as_user')
            rpc = request.GET.copy()
            del rpc['as_user']
            request.GET = rpc
            user = get_object_or_404(User, username=as_user)
            request.user = user

        if 'switch_user' in request.GET and (request.user.is_superuser or request.session.has_key('_switch_user')):
            request.session['_switch_user'] = True
            as_user = request.GET.get('switch_user')
            rpc = request.GET.copy()
            del rpc['switch_user']
            request.GET = rpc
            user = get_object_or_404(User, username=as_user)
            request.session['_auth_user_id'] = user.id
            request.user = user

        return None

