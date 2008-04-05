from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH

urlpatterns = patterns('',
    # Example:

    # main page
     (r'^$', 'hkn.main.views.main'),

    # other inclusions
    (r'^info/', include('hkn.info.urls')),
    (r'^event/', include('hkn.event.urls')),
    (r'^cand/', include('hkn.cand.urls')),
    (r'^resume/', include('hkn.resume.urls')),
    (r'^exam/', include('hkn.exam.urls')),
    (r'^tutor/', include('hkn.tutor.urls')),
    (r'^sms/', include('hkn.sms.urls')),
    (r'^yearbook/', include('hkn.yearbook.urls')),
    (r'^request/', include('hkn.request.urls')),    
    (r'^course/', include('hkn.course.urls')),        

    # authentication pages
     (r'^login/$', 'hkn.auth.login.login'),
     (r'^logout/$', 'hkn.auth.login.logout'),
     (r'^authenticate/$', 'hkn.auth.login.authenticate'),


     (r'^admin/', include('hkn.admin.urls')),


    # default static
    (r'^images/site/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static/images/site'}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': IMAGES_PATH}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static/css'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static/js'}),

)
    
