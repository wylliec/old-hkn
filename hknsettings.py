# the SERVER_ROOT variable no longer needs to be detected. It is detected automagically in settings.py

# the following are some variables that CAN be set here

DEBUG = True
#DEBUG = False

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'django_website_prod'             # Or path to database file if using sqlite3.
DATABASE_USER = 'django_website'             # Not used with sqlite3.
DATABASE_PASSWORD = 'monkey13'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'             # Set to empty string for default. Not used with sqlite3.

MEDIA_URL = 'http://hkn.eecs.berkeley.edu:8721/files/'
STATIC_PREFIX = 'http://hkn.eecs.berkeley.edu:8721/static/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://hkn.eecs.berkeley.edu:8721/static/admin/'


GCAL_ENABLED = True
GCAL_EMAIL = "hkn@hkn.eecs.berkeley.edu"
GCAL_PASSWORD = "a89Kl.o3"
# FORCE_LOGIN = False

EMAIL_HOST_USER = "gafyd"
EMAIL_HOST_PASSWORD = "shasha!!md5"

def setup_logger():
    import logging, logging.handlers

    formatter_simple = logging.Formatter("%(asctime)s %(message)s")
    formatter = logging.Formatter("%(asctime)s %(module)s:%(lineno)s %(levelname)s %(message)s")

    handler_root = logging.handlers.RotatingFileHandler('/var/log/django_root.log', "a", 5*1024*1024, 10)
    handler_root.setFormatter(formatter)
    handler_root.setLevel(logging.WARNING)

    handler_404 = logging.handlers.RotatingFileHandler('/var/log/django_404.log', "a", 2*1024*1024, 10)
    handler_404.setFormatter(formatter_simple)

    handler_access = logging.handlers.RotatingFileHandler('/var/log/django_access.log', "a", 2*1024*1024, 10)
    handler_access.setLevel(logging.INFO)
    handler_access.setFormatter(formatter_simple)

    handler_actions = logging.handlers.RotatingFileHandler('/var/log/django_actions.log', "a", 2*1024*1024, 10)
    handler_actions.setLevel(logging.INFO)
    handler_actions.setFormatter(formatter)

    handler_exceptions = logging.handlers.RotatingFileHandler('/var/log/django_exceptions.log', "a", 2*1024*1024, 10)
    handler_exceptions.setFormatter(formatter)

    logging.getLogger().addHandler(handler_root)
    logging.getLogger('special.actions').addHandler(handler_actions)
    logging.getLogger('special.404').addHandler(handler_404)
    logging.getLogger('special.access').addHandler(handler_access)
    logging.getLogger('special.exceptions').addHandler(handler_exceptions)
