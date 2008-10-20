#!/usr/bin/env python
import os, shutil, re
import hkn_settings
from django.conf import settings

cwd = settings.SERVER_ROOT

try:
	os.mkdir(cwd + "files/content/slideshow/")
except:
	pass

dest = cwd + "files/content/slideshow/"
for root, dirs, files in os.walk("/yearbook/public_html/slideshows/"):
	for name in files:
		shutil.copy(os.path.join(root, name), dest)
