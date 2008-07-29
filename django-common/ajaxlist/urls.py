from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add/$', 'ajaxlist.views.add', name='ajaxlist-add'),
    url(r'^remove/$', 'ajaxlist.views.remove', name='ajaxlist-remove'),
)