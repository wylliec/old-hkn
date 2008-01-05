from django.conf.urls.defaults import *

urlpatterns = patterns('',
		(r'^list/(?P<category>.*)/$', 'hkn.request.list.list_requests'),
		(r'^list/$', 'hkn.request.list.list_requests', {"category" : "actives"}),
		(r'^list_requests_ajax/$', 'hkn.request.list.list_requests_ajax'),		
		(r'^list_requests_confirm_ajax/(?P<request_id>.*)/$', 'hkn.request.list.list_requests_confirm_ajax'),								
		(r'^list_requests_confirm_ajax/$', 'hkn.request.list.list_requests_confirm_ajax'),				
	)					    
