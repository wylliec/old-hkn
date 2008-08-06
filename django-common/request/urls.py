from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^list/(?P<category>.*)/$', 'request.list.list_requests', name="request-list-category"),
        url(r'^list/$', 'request.list.list_requests', {"category" : "actives"}, name="request-list"),
        url(r'^list_requests_confirm_ajax/$', 'request.list.list_requests_confirm_ajax', name="request-ajax-confirm"),
    )                        
