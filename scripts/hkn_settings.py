from django.core.management import setup_environ
import django, sys

# import settings module from one directory down
sys.path.append("../..")
import hkn.settings
sys.path.remove("../..")

setup_environ(hkn.settings)

