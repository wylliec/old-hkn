from hkn.request.constants import REQUEST_TYPE
from hkn.request.models import Request


class HknRequestsWrapper(object):
    def __init__(self, user):
        self.user = user

    def __len__(self):
        return len(Request.actives.for_user(self.user))

def hkn_requests(request):
    """
    """
    return {
        'requests' : HknRequestsWrapper(request.user)
    }
