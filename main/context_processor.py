from hkn.settings import ROOT_URL, STATIC_PREFIX, MEDIA_URL
from hkn.main.property import PROPERTIES

def hkn_vars(request):
    layout = request.session.get("layout", "-green")
    return {
        "ROOT_URL" : "/" + ROOT_URL,
        "STATIC_PREFIX" : STATIC_PREFIX,
        "MEDIA_URL" : MEDIA_URL,
    	"LAYOUT"  : layout,
	    "LAYOUT_HTML" : "hkn" + layout + ".html",
        "DEFAULT_PICTURE" : "/static/images/site/lion.gif",
        "PROPERTIES" : PROPERTIES
	}




# PermWrapper and PermLookupDict proxy the permissions system into objects that
# the template system can understand.

class PermLookupDict(object):
    def __init__(self, user, module_name):
        self.user, self.module_name = user, module_name

    def __repr__(self):
        return str(self.user.get_all_permissions())

    def __getitem__(self, perm_name):
        return self.user.has_perm("%s.%s" % (self.module_name, perm_name))

    def __nonzero__(self):
        return self.user.has_module_perms(self.module_name)

class PermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, module_name):
        return PermLookupDict(self.user, module_name)


def auth(request):
    """
    Returns context variables required by apps that use Django's authentication
    system.
    """
    return {
        'user': request.user,
        'perms': PermWrapper(request.user),
    }


