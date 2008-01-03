from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^confirmed/$', 'hkn.cand.confirm.requirements'),		
		(r'^initiate/(?P<category>.*)/$', 'hkn.cand.initiate.initiate'),
		(r'^initiate/$', 'hkn.cand.initiate.initiate'),
		(r'^initiate_ajax/$', 'hkn.cand.initiate.initiate_ajax'),		
	)					    
