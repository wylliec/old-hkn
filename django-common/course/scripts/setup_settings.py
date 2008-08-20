from django.core.management import setup_environ
import django, sys
import os.path

PATH=os.path.expanduser("~/mu-site/hkn/")

def setup():
    sys.path.append(PATH)
    import settings
    sys.path.remove(PATH)
    print "USING SETTINGS FROM: %s" % (PATH,)

    setup_environ(settings)

def get_cd():
    return os.path.join(os.getcwd(), os.path.dirname(__file__))
    

