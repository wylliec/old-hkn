
__all__ = ['SMS_MODULES']
import os, os.path

SMS_MODULES = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py") and not f.endswith('__init__.py')]
SMS_MODULES.sort()

#SMS_MODULES = ['event', 'user']

