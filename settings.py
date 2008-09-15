##
##
##
##
##
# Please edit hknsettings.py to set local settings, not this file
##
##
##
##
##


#########################
# HKN-Specific Settings #
#########################

import os
SERVER_ROOT = os.path.join(os.getcwd(), os.path.dirname(__file__))

if SERVER_ROOT.endswith('hkn'):
    SERVER_ROOT = SERVER_ROOT + '/'

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = SERVER_ROOT + "hkn.db"            # Or path to database file if using sqlite3.

CACHE_BACKEND = 'locmem:///'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

EXAMS_USER_MODULE = 'django.contrib.auth.models.User'
EXAM_LOGIN_REQUIRED = False
LOGIN_URL = "/login/"
ACCOUNT_ACTIVATION_DAYS = 7

SESSION_SAVE_EVERY_REQUEST = True

#django-tagging setting
FORCE_LOWERCASE_TAGS = True

# don't change this
IMAGES_PATH = os.path.expanduser("~/hkn-website-images/")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/files/'
STATIC_PREFIX = '/static/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# django crap
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = SERVER_ROOT + "files/"


DJANGO_COMMON = SERVER_ROOT + "django-common/"


ADMINS = (
#     ('HKN Computing Services', 'compserv@hkn.eecs.berkeley.edu'),
)

DEFAULT_FROM_EMAIL = "hkn@hkn.eecs.berkeley.edu"
EMAIL_HOST = "hkn.eecs.berkeley.edu"
EMAIL_PORT= 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True

LOGGING_INTERCEPT_REDIRECTS = True
LOGGING_LOG_SQL = True
LOGGING_SHOW_METRICS = True
LOGGING_OUTPUT_ENABLED = False

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

# this site's ID
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

LOGIN_REDIRECT_URL = "/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'bb39p31)!7=far+)+wxz@mg*5v#g*!35ivju#^5t3l!y*2(76*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'hkn.main.middleware.HknAuthMiddleware',
    'hkn.main.middleware.LayoutMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'djangologging.middleware.LoggingMiddleware',
    'djangodblog.DBLogMiddleware',
)

ROOT_URLCONF = 'hkn.main.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SERVER_ROOT + "templates"
)

TEMPLATE_CONTEXT_PROCESSORS = (
"hkn.main.context_processor.hkn_vars",
"request.context_processor.requests",
#"hkn.gcal.context_processor.gcal",
"django.core.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.request",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.webdesign',
    'ajaxlist',
    'request',
    'hkn.info',
    'hkn.gcal',
    'hkn.event',
#    'hkn.cand',
#    'hkn.yearbook',
    'exam',
    'hkn.tutor',
    'hkn.main',
    'hkn.indrel',
    'course',
    'tagging',
    'review',
    'photologue',
    'registration',
    'nice_types',
    'djangodblog',
    'resume',
#    'south',
)

AUTHENTICATION_BACKENDS = (
    'hkn.main.pam_backend.PamBackend',
    'django.contrib.auth.backends.ModelBackend',
)

DBLOG_CATCH_404_ERRORS = True
GCAL_ENABLED = False
GCAL_EMAIL = "hkn-test@hkn.eecs.berkeley.edu"
GCAL_PASSWORD = "monkey13"

# hknsettings settings will override the above
from hknsettings import *

# make sure SERVER_ROOT ends with hkn/
if not SERVER_ROOT.endswith("hkn/"):
    raise Exception, "Your SERVER_ROOT is configured incorrectly in /hkn/settings.py. Make sure it ends with \"hkn/\" (including the final slash)"

