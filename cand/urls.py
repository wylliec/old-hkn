from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^upload-eligibility-list/$', 'hkn.cand.views.upload_eligibility_list', name='cand-upload-eligibility-list'),
    url(r'^process-eligibility-list/$', 'hkn.cand.views.process_eligibility_list', name='cand-process-eligibility-list'),
    url(r'^dump-candidate-emails/(?P<category>.*)/$', 'hkn.cand.views.dump_candidate_emails', name='cand-dump-candidate-emails'),
    url(r'^portal/$', 'hkn.cand.views.portal', name='cand-portal'),
    url(r'^application/$', 'hkn.cand.views.application', name='cand-application'),
    url(r'^portal/create_challenge_ajax/$', 'hkn.cand.views.create_challenge_ajax', name='challenge-create-ajax'),
    url(r'^portal/create_challenge/$', 'hkn.cand.views.create_challenge', name='challenge-create'),
    url(r'^vp_event_confirm/$', 'hkn.cand.views.event_confirmation', name='vp-event-confirm'),
    )					    
