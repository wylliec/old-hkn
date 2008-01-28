from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'hkn.tutor.views.schedule'),
#    (r'^$', 'hkn.tutor.views.signup'),
    (r'^contact/$', 'hkn.tutor.views.contact'),
    (r'^feedback/$', 'hkn.tutor.views.feedback'),
    (r'^signup/$', 'hkn.tutor.views.signup'),
    (r'^submit_signup/$', 'hkn.tutor.views.submit_signup'),
    (r'^view_signups/$', 'hkn.tutor.views.view_signups'),
    (r'^submit_assignments/$', 'hkn.tutor.views.submit_assignments'),
    (r'^admin/$', 'hkn.tutor.views.admin'),
    )
