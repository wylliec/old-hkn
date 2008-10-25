from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'hkn.yearbook.views.main', name="yearbook-gallery"),
    url(r'^(?P<semester>(sp|fa)\d{2})/$', 'hkn.yearbook.views.semester', name="yearbook-gallery-semester"),
    url(r'^(?P<semester>(sp|fa)\d{2})/page/(?P<page>[0-9]+)/$', 'hkn.yearbook.views.semester', name="yearbook-gallery-semester-list"),
    (r'^', include('photologue.urls')),
    )
