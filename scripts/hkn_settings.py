from django.core.management import setup_environ
import django, sys

# import settings module from one directory down
sys.path.append("../..")
import hkn.settings
sys.path.remove("../..")
sys.path.append("/home/hzarka/django-common/")

setup_environ(hkn.settings)

