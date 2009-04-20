from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^upload-eligibility-list/$', 'hkn.cand.views.upload_eligibility_list', name='cand-upload-eligibility-list'),
    url(r'^process-eligibility-list/$', 'hkn.cand.views.process_eligibility_list', name='cand-process-eligibility-list'),
    url(r'^dump-candidate-emails/(?P<category>.*)/$', 'hkn.cand.views.dump_candidate_emails', name='cand-dump-candidate-emails'),
    url(r'^portal/$', 'hkn.cand.views.portal', name='cand-portal'),
    url(r'^application/$', 'hkn.cand.views.application', name='cand-application'),
    url(r'^view-applications/$', 'hkn.cand.views.view_applications', name='cand-view-applications'),
    url(r'^portal/create_challenge_ajax/$', 'hkn.cand.views.create_challenge_ajax', name='challenge-create-ajax'),
    url(r'^portal/create_challenge/$', 'hkn.cand.views.create_challenge', name='challenge-create'),
    url(r'^vp_event_confirm/$', 'hkn.cand.views.event_confirmation', name='vp-event-confirm'),
    url(r'^all_candidates_events/$', 'hkn.cand.views.all_candidates_events', name='all-candidates-events'),
    url(r'^all_candidates_events3/$', 'hkn.cand.views.all_candidates_events', name='all-candidates-events3'),
#    url(r'^course_survey_signup/$', 'hkn.cand.views.course_survey_signup', name='cand-survey-signup'),
#    url(r'^course_survey_add_courses/$', 'hkn.cand.views.course_survey_add_courses', name='cand-survey-add-courses'),
    url(r'^quiz/$', 'hkn.cand.views.candidate_quiz', name='cand-quiz'),
    url(r'^view_quiz_submissions/$', 'hkn.cand.views.view_quiz_submissions', name='cand-view-quiz-submissions'),
    )					    
