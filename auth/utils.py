from hkn.auth.models import *

PERSONID_KEY = 'person_id'
LOGIN_URL = '/login/'
REDIRECT_FIELD_NAME = 'next'

def authenticate(username=None, password=None):
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        return None

def get_user_for_id(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None

def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    request.session[PERSONID_KEY] = user.person_id

def logout(request):
    """
    Remove the authenticated user's ID from the request.
    """
    try:
        del request.session[PERSONID_KEY]
    except KeyError:
        pass

def get_user(request):
    try:
        user_id = request.session[PERSONID_KEY]
        user = get_user_for_id(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user
