from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^upload-eligibility-list/$', 'hkn.cand.views.upload_eligibility_list', name='cand-upload-eligibility-list'),
    url(r'^process-eligibility-list/$', 'hkn.cand.views.process_eligibility_list', name='cand-process-eligibility-list'),
    url(r'^portal/$', 'hkn.cand.views.portal', name='cand-portal'),
    )					    
