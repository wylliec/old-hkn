from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH, MEDIA_ROOT, MEDIA_URL, DJANGO_COMMON
from hkn.main.admin import admin_site

urlpatterns = patterns('',
    # Example:

    # main page
     (r'^$', 'hkn.main.views.main'),
     (r'^css/hkn-(?P<css_file>\w*).css$', 'hkn.main.themes.theme_css'),

    # other inclusions
    (r'^ajaxlist/', include('ajaxlist.urls')),
    (r'^info/', include('hkn.info.urls')),
    (r'^event/', include('hkn.event.urls')),
    (r'^cand/', include('hkn.cand.urls')),
    (r'^resume/', include('hkn.resume.urls')),
    (r'^exam/', include('exam.urls')),
    (r'^review/', include('review.urls')),
    (r'^tutor/', include('hkn.tutor.urls')),
    (r'^sms/', include('hkn.sms.urls')),
    (r'^yearbook/', include('photologue.urls')),
    (r'^request/', include('request.urls')),    
    (r'^course/', include('course.urls')),        
    (r'^account/', include('registration.urls')),        

    # authentication pages
     url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
     url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),

     (r'^admin/(.*)', admin_site.root),

    # default static
    (r'^static/ajaxlist/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/ajaxlist/media'}),
    (r'^static/exam/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/exam/media'}),
    (r'^static/request/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/request/media'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static'}),

    # media
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
