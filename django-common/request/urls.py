from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^list/(?P<category>.*)/$', 'request.list.list_requests'),
        (r'^list/$', 'request.list.list_requests', {"category" : "actives"}),
        (r'^list_requests_ajax/$', 'request.list.list_requests_ajax'),		
        (r'^list_requests_confirm_ajax/(?P<request_id>.*)/$', 'request.list.list_requests_confirm_ajax'),								
        url(r'^list_requests_confirm_ajax/$', 'request.list.list_requests_confirm_ajax', name="request-ajax-confirm"),
    )					    
