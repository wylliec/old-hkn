#!/usr/bin/env python
import hkn_settings

from django.db.models import loading
from django.core.management import call_command

def main():
    for app in loading.get_apps():
    	if app.__name__.endswith("markup.models"):
		continue
        call_command('reset', app.__name__.split('.')[-2], noinput=True)
    
    call_command('flush')
    call_command('syncdb')

if __name__ == "__main__":
    main()
