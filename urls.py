from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH

urlpatterns = patterns('',
    # Example:
    # (r'^hkn/', include('hkn.foo.urls')),

      (r'^$', 'hkn.main.views.main'),

     (r'^hkn/', include('hkn.info.urls')),
     (r'^login/$', 'hkn.auth.login.login'),
     (r'^logout/$', 'hkn.auth.login.logout'),
     (r'^authenticate/$', 'hkn.auth.login.authenticate'),

    # other inclusions
    (r'^info/', include('hkn.info.urls')),
    (r'^event/', include('hkn.event.urls')),
    (r'^cand/', include('hkn.cand.urls')),

    # default static
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': IMAGES_PATH}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static/css'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': SERVER_ROOT + '/static/js'}),

)
    
