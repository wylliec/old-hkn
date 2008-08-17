from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'hkn.tutor.views.schedule', name="tutor-view-schedule"),
    url(r'^signup/$', 'hkn.tutor.views.signup', name="tutor-signup"),
    url(r'^submit_signup/$', 'hkn.tutor.views.submit_signup'),
    url(r'^view_signups/$', 'hkn.tutor.views.view_signups', name="tutor-view-signups"),
    (r'^submit_assignments/$', 'hkn.tutor.views.submit_assignments'),
    url(r'^admin/$', 'hkn.tutor.views.admin', name="tutor-admin"),
    (r'^admin/params_for_scheduler/$', 'hkn.tutor.views.params_for_scheduler'),
    (r'^admin/submit_schedule/$', 'hkn.tutor.views.submit_schedule'),
    (r'^tutor_list/$', 'hkn.tutor.views.tutor_list'),
    (r'^availabilities_table/$', 'hkn.tutor.views.availabilities_table'),
    )
