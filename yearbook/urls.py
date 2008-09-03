from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'hkn.yearbook.views.main'),
    (r'^', include('photologue.urls')),
    )                        
