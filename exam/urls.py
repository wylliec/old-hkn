from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH

urlpatterns = patterns('',
    # Example:

    # main page
    (r'^$', 'hkn.exam.views.main'),
    (r'^faq/$', 'hkn.exam.views.faq'),
    (r'^committee/$', 'hkn.exam.views.committee'),
    (r'^onlineexams/$', 'hkn.exam.views.onlineexams'),
    (r'^submit/$', 'hkn.exam.views.submit'),
)
