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

    url(r'^quiz/$', 'hkn.cand.views.candidate_quiz', name='cand-quiz'),
    url(r'^view_quiz_submissions/$', 'hkn.cand.views.view_quiz_submissions', name='cand-view-quiz-submissions'),
    url(r'^view_quiz_submissions/(?P<quiz_id>.*)/$', 'hkn.cand.views.view_quiz', name='cand-view-quiz'),
    url(r'^rescore_quizzes/$', 'hkn.cand.views.rescore_quizzes', name='cand-rescore-quizzes'),

    url(r'^course_survey_admin/$', 'hkn.cand.views.course_survey_admin', name='course-survey-admin'),
    url(r'^course_survey_admin/select_classes/$', 'hkn.cand.views.course_survey_admin_select_classes', name='course-survey-select-classes'),
    url(r'^course_survey_admin/select_classes_ajax/$', 'hkn.cand.views.course_survey_select_ajax', name='course-survey-select-ajax'),
    url(r'^course_survey_admin/manage/$', 'hkn.cand.views.course_survey_admin_manage', name='course-survey-admin-manage'),

    url(r'^course_survey_signup/$', 'hkn.cand.views.course_survey_signup', name='course-survey-signup'),
    )					    
