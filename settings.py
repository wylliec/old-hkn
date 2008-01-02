# Django settings for hkn project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('HKN Computing Services', 'compserv@hkn.eecs.berkeley.edu'),
)

# a valid value should look something like this:
SERVER_ROOT = "/home/hzarka/website/hkn/"
# SERVER_ROOT = "/dev/null"


# make sure SERVER_ROOT ends with hkn/
if not SERVER_ROOT.endswith("hkn/"):
	raise Exception, "Your SERVER_ROOT is configured incorrectly in /hkn/settings.py. Make sure it ends with \"hkn/\" (including the final slash)"

#don't change this
IMAGES_PATH = "/home/hzarka/hkn-website-images/"

MANAGERS = ADMINS

#DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
#DATABASE_NAME = 'hzarka_hkn'             # Or path to database file if using sqlite3.
#DATABASE_USER = 'hzarka'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'monkey13'         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = SERVER_ROOT + "hkn.db"            # Or path to database file if using sqlite3.


# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

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
    'hkn.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'hkn.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SERVER_ROOT + "templates"
)

TEMPLATE_CONTEXT_PROCESSORS = (
"hkn.auth.context_processor.auth",
"hkn.gcal.context_processor.gcal",
#"django.core.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n")

INSTALLED_APPS = (
#    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
#    'django.contrib.admin',
    'hkn.info',
    'hkn.auth',
    'hkn.sms',
    'hkn.event',
    'hkn.gcal',
    'hkn.cand',
    'hkn.yearbook',
    'hkn.exam',
    'hkn.tutor',
    'hkn.resume',
)
