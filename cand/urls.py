from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^confirmed/$', 'hkn.cand.confirm.requirements'),
		(r'^confirm/$', 'hkn.cand.confirm.list'),
		(r'^initiate/$', 'hkn.cand.initiate.initiate'),
		(r'^confirm/(?P<event_id>.*)/$', 'hkn.cand.confirm.confirm'),
	)					    
