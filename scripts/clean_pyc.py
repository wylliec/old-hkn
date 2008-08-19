#!/usr/bin/env python
import os

cwd = os.getcwd()
if cwd.endswith('scripts'):
	cwd = cwd[:-7]
for root, dirs, files in os.walk(cwd):
	for file in files:
		if file.endswith('pyc'):
			print 'deleting', os.path.join(root, file)
			os.remove(os.path.join(root, file))

