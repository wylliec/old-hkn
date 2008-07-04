from request.constants import REQUEST_TYPE
from request.models import Request


class RequestsWrapper(object):
    def __init__(self, user):
        self.user = user

    def __len__(self):
        return len(Request.actives.for_user(self.user))

def requests(request):
    """
    """
    return {
        'requests' : RequestsWrapper(request.user)
    }
