#!/usr/bin/env python
import os
import hkn_settings
from django.conf import settings

cwd = settings.SERVER_ROOT
for root, dirs, files in os.walk(cwd):
	for file in files:
		if file.endswith('.pyc'):
			print 'deleting', os.path.join(root, file)
			os.remove(os.path.join(root, file))

