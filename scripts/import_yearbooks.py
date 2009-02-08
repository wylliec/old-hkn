#!/usr/bin/env python
import os, shutil, re
import hkn_settings
from django.conf import settings

cwd = settings.SERVER_ROOT

try:
	os.mkdir(cwd + "files/content/yearbook/")
except:
	pass

dest = cwd + "files/content/yearbook/"
for root, dirs, files in os.walk("/yearbook/public_html/yearbooks/"):
	for name in files:
		if re.match("yearbook-.*\\.pdf$", name):
			shutil.copy(os.path.join(root, name), dest)
