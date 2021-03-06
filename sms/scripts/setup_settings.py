import os, sys, re

# stop after reaching '/' on nix or 'C:\' on Windows
top_level_rx = re.compile(r'^(/|[a-zA-Z]:\\)$')
def is_top_level(path):
   return top_level_rx.match(path) is not None

def get_scripts_directory():
    return os.path.join(os.getcwd(), os.path.dirname(__file__))

def prepare_environment():
   # we'll need this script's directory for searching purposess
   curdir, curfile = os.path.split(os.path.abspath(__file__))

   # move up one directory at a time from this script's
   # path, searching for settings.py
   settings_module = None
   while not settings_module:
      try:
         sys.path.append(curdir)
         settings_module = __import__('settings', {}, {}, [''])
         sys.path.pop()
         break
      except ImportError:
         settings_module = None

      # have we reached the top-level directory?
      if is_top_level(curdir):
         raise Exception("settings.py was not found in the script's directory or any of its parent directories.")

      # move up a directory
      curdir = os.path.normpath(os.path.join(curdir, '..'))

   # set up the environment using the settings module
#   print "USING SETTINGS FROM: %s" % (curdir,)
   from django.core.management import setup_environ
   setup_environ(settings_module)
   from django.conf import settings
   sys.path.append(settings.DJANGO_COMMON)

prepare_environment()
