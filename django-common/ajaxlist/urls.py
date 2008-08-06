from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ajaxlist.views.post', name='ajaxlist-post'),
)
