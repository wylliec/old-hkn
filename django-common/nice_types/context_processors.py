from django.contrib.sites.models import Site
from django.conf import settings

try:
    _current_site = Site.objects.get_current()
except Site.DoesNotExist:
    _current_site = ''
def current_site(request):
    return { 'site': _current_site }

_STATIC_URL = { 'STATIC_URL': getattr(settings, 'STATIC_URL', settings.MEDIA_URL) }
def static_url(request):
    return _STATIC_URL
