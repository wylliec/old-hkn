from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH, MEDIA_ROOT, MEDIA_URL, DJANGO_COMMON
from hkn.main.admin import admin_site

urlpatterns = patterns('',
    # Example:

    # main page
     url(r'^$', 'hkn.main.views.main', name='hkn-landing-page'),
     (r'^css/hkn-(?P<css_file>\w*).css$', 'hkn.main.themes.theme_css'),

    # other inclusions
    (r'^ajaxlist/', include('ajaxlist.urls')),
    (r'^info/', include('hkn.info.urls')),
    (r'^event/', include('hkn.event.urls')),
    (r'^exam/', include('exam.urls')),
    (r'^review/', include('review.urls')),
    (r'^tutor/', include('hkn.tutor.urls')),
    (r'^sms/', include('hkn.sms.urls')),
    (r'^about/gallery/', include('hkn.yearbook.urls')),
    (r'^request/', include('request.urls')),    
    (r'^course/', include('course.urls')),        
    (r'^resume/', include('resume.urls')),
    (r'^indrel/', include('hkn.indrel.urls')),
    (r'^cand/', include('hkn.cand.urls')),
    (r'^account/', include('registration.urls')),        
    (r'^admin/', include('hkn.admin.urls')),
    # authentication pages
     url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
     url(r'^logout/$', 'hkn.main.views.logout', name="logout"),

   url(r'^password-reset/$', 'django.contrib.auth.views.password_reset', name='auth_password_reset'),
   url(r'^password-reset/done/$', 'django.contrib.auth.views.password_reset_done', name='auth_password_reset_done'),
   url(r'^password-confim-reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='auth_password_reset_confirm'),
   url(r'^password-confim-reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='auth_password_reset_complete'),
        

     (r'^admin/(.*)', admin_site.root),

    # default static
    (r'^static/ajaxlist/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/ajaxlist/media'}),
    (r'^static/exam/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/exam/media'}),
    (r'^static/request/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/request/media'}),
    (r'^static/nice_types/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DJANGO_COMMON + '/nice_types/media'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + 'static'}),
    (r'^favicon.ico$', 'django.views.static.serve', {'document_root': SERVER_ROOT, 'path' : 'static/favicon.ico'}),
    (r'^robots.txt$', 'django.views.static.serve', {'document_root': SERVER_ROOT, 'path' : 'static/robots.txt'}),

    # media
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
