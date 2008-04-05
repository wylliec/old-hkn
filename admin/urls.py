from django.conf import settings
from django.conf.urls.defaults import *

if settings.USE_I18N:
    i18n_view = 'django.views.i18n.javascript_catalog'
else:
    i18n_view = 'django.views.i18n.null_javascript_catalog'

urlpatterns = patterns('',
    ('^$', 'hkn.admin.views.main.index'),
    ('^r/', include('django.conf.urls.shortcut')),
    ('^jsi18n/$', i18n_view, {'packages': 'django.conf'}),
    ('^logout/$', 'hkn.auth.login.logout'),
#    ('^password_change/$', 'django.contrib.auth.views.password_change'),
#    ('^password_change/done/$', 'django.contrib.auth.views.password_change_done'),
    ('^template_validator/$', 'hkn.admin.views.template.template_validator'),

    # Documentation
    ('^doc/$', 'hkn.admin.views.doc.doc_index'),
    ('^doc/bookmarklets/$', 'hkn.admin.views.doc.bookmarklets'),
    ('^doc/tags/$', 'hkn.admin.views.doc.template_tag_index'),
    ('^doc/filters/$', 'hkn.admin.views.doc.template_filter_index'),
    ('^doc/views/$', 'hkn.admin.views.doc.view_index'),
    ('^doc/views/(?P<view>[^/]+)/$', 'hkn.admin.views.doc.view_detail'),
    ('^doc/models/$', 'hkn.admin.views.doc.model_index'),
    ('^doc/models/(?P<app_label>[^\.]+)\.(?P<model_name>[^/]+)/$', 'hkn.admin.views.doc.model_detail'),
#    ('^doc/templates/$', 'django.views.admin.doc.template_index'),
    ('^doc/templates/(?P<template>.*)/$', 'hkn.admin.views.doc.template_detail'),

    # "Add user" -- a special-case view
    ('^auth/user/add/$', 'hkn.admin.views.auth.user_add_stage'),
    # "Change user password" -- another special-case view
    ('^auth/user/(\d+)/password/$', 'hkn.admin.views.auth.user_change_password'),

    # Add/change/delete/history
    ('^([^/]+)/([^/]+)/$', 'hkn.admin.views.main.change_list'),
    ('^([^/]+)/([^/]+)/add/$', 'hkn.admin.views.main.add_stage'),
    ('^([^/]+)/([^/]+)/(.+)/history/$', 'hkn.admin.views.main.history'),
    ('^([^/]+)/([^/]+)/(.+)/delete/$', 'hkn.admin.views.main.delete_stage'),
    ('^([^/]+)/([^/]+)/(.+)/$', 'hkn.admin.views.main.change_stage'),
)

del i18n_view
