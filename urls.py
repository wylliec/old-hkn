from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH, ROOT_URL

urlpatterns = patterns('',
    (r'^' + ROOT_URL, include('hkn.main.urls')))

