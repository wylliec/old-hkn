from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^upload-eligibility-list/$', 'hkn.cand.views.upload_eligibility_list', name='cand-upload-eligibility-list'),
    url(r'^process-eligibility-list/$', 'hkn.cand.views.process_eligibility_list', name='cand-process-eligibility-list'),
    url(r'^portal/$', 'hkn.cand.views.portal', name='cand-portal'),
    url(r'^portal/create_challenge_ajax/$', 'hkn.cand.views.create_challenge_ajax', name='challenge-create-ajax'),
    url(r'^portal/create_challenge/$', 'hkn.cand.views.create_challenge', name='challenge-create'),
    )					    
