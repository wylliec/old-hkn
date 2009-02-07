#!/usr/bin/env python
import hkn_settings

from django.db.models import loading
from django.core.management import call_command

def main():
    call_command('syncdb')
    return
    for app in loading.get_apps():
    	for ends in ("markup.models", "webdesign.models"):
    		if app.__name__.endswith(ends):
			continue
        call_command('reset', app.__name__.split('.')[-2], noinput=True)
    
    call_command('flush')
    call_command('syncdb')

if __name__ == "__main__":
    main()
