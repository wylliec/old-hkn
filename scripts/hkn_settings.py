from django.core.management import setup_environ
import django, sys

sys.path.append("/home/hzarka")

import hkn.settings
setup_environ(hkn.settings)
