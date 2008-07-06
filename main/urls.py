from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH

urlpatterns = patterns('',
    # Example:

    # main page
     (r'^$', 'hkn.main.views.main'),
     (r'^css/hkn-(?P<css_file>\w*).css$', 'hkn.main.themes.theme_css'),

    # other inclusions
    (r'^info/', include('hkn.info.urls')),
    (r'^event/', include('hkn.event.urls')),
    (r'^cand/', include('hkn.cand.urls')),
    (r'^resume/', include('hkn.resume.urls')),
    (r'^exam/', include('exam.urls')),
    (r'^review/', include('review.urls')),
    (r'^tutor/', include('hkn.tutor.urls')),
    (r'^sms/', include('hkn.sms.urls')),
    (r'^yearbook/', include('hkn.yearbook.urls')),
    (r'^request/', include('request.urls')),    
    (r'^course/', include('course.urls')),        

    # authentication pages
     (r'^login/$', 'hkn.auth.login.login'),
     (r'^logout/$', 'hkn.auth.login.logout'),
     (r'^authenticate/$', 'hkn.auth.login.authenticate'),


     #(r'^admin/', include('hkn.admin.urls')),


    # default static
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static'}),

    # media
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/files'}),

)
    
