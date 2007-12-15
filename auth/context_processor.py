

def auth(request):
    """
    Returns context variables required by apps that use Django's authentication
    system.
    """
    return {
        'user': request.user,
        'perms': PermWrapper(request.user),
    }


class PermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, item):
        return self.user.has_perm(item)

