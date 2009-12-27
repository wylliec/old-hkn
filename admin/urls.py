from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'^tutor/', include('hkn.tutor.urls')),
    (r'^request/', include('request.urls')), 
    )                        
