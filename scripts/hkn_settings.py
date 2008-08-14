from django.core.management import setup_environ
import django, sys

# import settings module from one directory down
sys.path.append("../..")
import hkn.settings
sys.path.remove("../..")
sys.path.append(hkn.settings.DJANGO_COMMON)

setup_environ(hkn.settings)

