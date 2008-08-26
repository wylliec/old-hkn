from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'hkn.tutor.views.schedule', name="tutor-view-schedule"),
    url(r'^signup/$', 'hkn.tutor.admin_views.signup', name="tutor-signup"),
    url(r'^submit_signup/$', 'hkn.tutor.admin_views.submit_signup', name="tutor-submit-signup"),
    url(r'^view_signups/$', 'hkn.tutor.admin_views.view_signups', name="tutor-view-signups"),
    url(r'^submit_assignments/$', 'hkn.tutor.admin_views.submit_assignments', name="tutor-submit-assignments"),
    url(r'^admin/$', 'hkn.tutor.admin_views.admin', name="tutor-admin"),
    (r'^admin/params_for_scheduler/$', 'hkn.tutor.admin_views.params_for_scheduler'),
    url(r'^admin/submit_schedule/$', 'hkn.tutor.admin_views.submit_schedule', name="tutor-submit-schedule"),
    (r'^tutor_list/$', 'hkn.tutor.admin_views.tutor_list'),
    (r'^availabilities_table/$', 'hkn.tutor.admin_views.availabilities_table'),
    )
