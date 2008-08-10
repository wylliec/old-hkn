from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^/$', 'ajaxlist.views.post_ajax', name='ajaxlist-post-ajax'),
	url(r'^post$', 'ajaxlist.views.post', name='ajaxlist-post'), 
	url(r'^clear$', 'ajaxlist.views.clear', name='ajaxlist-clear'),
)
